import datetime

geoformat_field_type_to_python_type = {
    "Integer": int,
    "IntegerList": (int, list),
    "Real": float,
    "RealList": (float, list),
    "String": str,
    "StringList": (str, list),
    "Binary": bytes,
    "Date": datetime.date,
    "Time": datetime.time,
    "DateTime": datetime.datetime,
    "Boolean": bool,
}

geoformat_field_type_to_postgresql_type = {
    "Integer": "integer",
    "IntegerList": "integer[]",
    "Real": "numeric",
    "RealList": "numeric[]",
    "String": "character varying",
    "StringList": "character varying[]",
    "Binary": "bytea",
    "Date": "date",
    "Time": "time",
    "DateTime": "timestamp",
    "Boolean": "boolean",
}

geoformat_field_type_to_geojson_field_type = {
    "Binary": str,
    "Date": str,
    "Time": str,
    "DateTime": str,
}


shapefile_str_max_width = 250
geoformat_field_type_to_shapefile_field_type = {
    "Integer": "N",
    "IntegerList": None,
    "Real": "N",
    "RealList": None,
    "String": "C",
    "StringList": None,
    "Binary": None,
    "Date": "D",
    "Time": "C",
    "DateTime": "C",
    "Boolean": "L",
}

"""

    "C": Characters, text.
    "N": Numbers, with or without decimals.
    "F": Floats (same as "N").
    "L": Logical, for boolean True/False values.
    "D": Dates.
    "M": Memo, has no meaning within a GIS and is part of the xbase spec instead.

"""

shapefile_field_type_to_geoformat_field_type = {
    "C": "String",
    "N": "Real",
    "Float": "Real",
    "L": "Boolean",
    "D": "Date"
}

# all in str except String itself
geoformat_field_type_to_csv_field_type = {
    "Integer": str,
    "IntegerList": str,
    "Real": str,
    "RealList": str,
    "StringList": str,
    "Binary": str,
    "Date": str,
    "Time": str,
    "DateTime": str,
    "Boolean": str,
}

python_type_to_geoformat_field_type = {
    str: "String",
    (str, list): "StringList",
    float: "Real",
    (float, list): "RealList",
    int: "Integer",
    (int, list): "IntegerList",
    datetime.date: "Date",
    datetime.time: "Time",
    datetime.datetime: "DateTime",
    bytes: "Binary",
    bool: "Boolean",
}

recast_black_list = {
    "Integer": {"Binary"},
    "IntegerList": {"Real", "Integer", "Binary", "Date", "Time", "DateTime", "Boolean"},
    "Real": {"Binary"},
    "RealList": {"Integer", "Real", "Binary", "Date", "Time", "DateTime", "Boolean"},
    "String": {"Date", "Time", "DateTime"},
    "StringList": {"Integer", "Real", "Binary", "Date", "Time", "DateTime", "Boolean"},
    "Date": {
        "Binary",
        "Time",
        "DateTime",
    },
    "Time": {
        "Binary",
        "Date",
        "DateTime",
    },
    "DateTime": {
        "Binary"
    },
    "Binary": {
        "Integer",
        "IntegerList",
        "Real",
        "RealList",
        "Date",
        "Time",
        "DateTime",
    },
    "Boolean": {"IntegerList", "RealList", "StringList", "Date", "Time", "DateTime"},
}
ogr_field_type_to_geoformat_field_type = {
    0: "Integer",
    1: "IntegerList",
    2: "Real",
    3: "RealList",
    4: "String",
    5: "StringList",
    6: "String",  # WideString
    7: "StringList",  # WideStringList
    8: "Binary",
    9: "Date",
    10: "Time",
    11: "DateTime",
}

field_type_set = {
    "Integer",
    "IntegerList",
    "Real",
    "RealList",
    "String",
    "StringList",
    "Binary",
    "Date",
    "Time",
    "DateTime",
    "Boolean",
}
field_metadata_width_required = {"Real", "RealList", "String", "StringList"}
field_metadata_precision_required = {"Real", "RealList"}
none_value_pattern = {None}
