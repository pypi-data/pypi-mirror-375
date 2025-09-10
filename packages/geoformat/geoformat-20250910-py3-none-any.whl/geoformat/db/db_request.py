try:
    from osgeo import ogr
    from osgeo import osr
    import_ogr_success = True
except ImportError:
    import_ogr_success = False

from geoformat.driver.ogr.ogr_driver import ogr_layer_to_geolayer

from geoformat.conf.error_messages import import_ogr_error

def sql(
        sql_request,
        host,
        database_name,
        user,
        password,
        port=5432,
    ):
    """
    Execute an SQL request on the specified PostgreSQL database using GDAL/OGR.

    :param sql_request: SQL request as a string.
    :param host: Host address of the PostgreSQL server.
    :param database_name: Name of the database.
    :param user: Username for the database connection.
    :param password: Password for the database connection.
    :param port: Port number for the database connection (default is 5432).
    :return: Result of the SQL request execution from OGR.
    :raises Exception: If OGR import fails.
    """
    pg_adress = f"PG: host={host} dbname={database_name} user={user} password={password} port={port}"
    if import_ogr_success is True:
        data_source = ogr.Open(pg_adress)
        return data_source.ExecuteSQL(sql_request)
    else:
        raise Exception(import_ogr_error)


def sql_select_to_geolayer(
    select_request,
    host,
    database_name,
    user,
    password,
    port=5432,
    geolayer_name=None,
    field_name_filter=None,
    bbox_extent=True,
    bbox_filter=None,
    feature_serialize=False,
    feature_limit=None,
    feature_offset=None
):
    """
    Execute a SQL SELECT request on the specified PostgreSQL database and return the result as a geolayer.

    :param select_request: SQL SELECT request as a string.
    :param host: Host address of the PostgreSQL server.
    :param database_name: Name of the database.
    :param user: Username for the database connection.
    :param password: Password for the database connection.
    :param port: Port number for the database connection (default is 5432).
    :param geolayer_name: Optional name for the resulting geolayer.
    :param field_name_filter: Optional filter for field names.
    :param bbox_extent: Boolean indicating whether to use bounding box extent (default is True).
    :param bbox_filter: Optional bounding box filter.
    :param feature_serialize: Boolean indicating whether to serialize features (default is False).
    :param feature_limit: Optional limit for the number of features.
    :param feature_offset: Optional offset for the features.
    :return: A geolayer resulting from the given SQL SELECT request.
    """
    # drop view if exists
    sql_drop_view = """DROP VIEW IF EXISTS geoformat_temporary_view;"""
    sql(sql_drop_view, host, database_name, user, password, port)
    # create view request
    sql_create_view = f"""CREATE OR REPLACE VIEW geoformat_temporary_view AS (
    {select_request}
    );"""
    # execute request
    sql(sql_create_view, host, database_name, user, password, port)

    pg_adress = f"PG: host={host} dbname={database_name} user={user} password={password} port={port}"
    geolayer = ogr_layer_to_geolayer(
        pg_adress,
        layer_id_or_name='geoformat_temporary_view',
        field_name_filter=field_name_filter,
        bbox_extent=bbox_extent,
        bbox_filter=bbox_filter,
        serialize=feature_serialize,
        feature_limit=feature_limit,
        feature_offset=feature_offset
    )

    if geolayer_name:
        geolayer['metadata']['name'] = geolayer_name
    # drop the view
    sql_drop_view = """DROP VIEW geoformat_temporary_view;"""
    sql(sql_drop_view, host, database_name, user, password, port)

    return geolayer
