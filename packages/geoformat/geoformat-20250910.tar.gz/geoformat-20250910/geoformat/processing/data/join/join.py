from geoformat.conf.error_messages import (
    geolayer_attributes_missing,
    field_missing,
    geometry_ref_geolayer,
)
from geoformat.index.attributes.hash import create_attribute_index
from geoformat.processing.data.join.merge_objects import merge_metadata, merge_feature
from geoformat.processing.data.union import union_geolayer
from geoformat.manipulation.geolayer_manipulation import (
    add_attributes_index,
    check_attributes_index,
    delete_attributes_index,
)

from geoformat.processing.data.clauses import clause_where
from geoformat.conversion.geolayer_conversion import create_geolayer_from_i_feat_list


def _check_input_geolayer_data(geolayer_a, geolayer_b, on_field_a, on_field_b):
    # check input data
    if "fields" in geolayer_a["metadata"]:
        if on_field_a not in geolayer_a["metadata"]["fields"]:
            raise Exception(field_missing.format(field_name=on_field_a))
    else:
        raise Exception(
            geolayer_attributes_missing.format(
                geolayer_name=geolayer_a["metadata"]["name"]
            )
        )

    if "fields" in geolayer_b["metadata"]:
        if on_field_b not in geolayer_b["metadata"]["fields"]:
            raise Exception(field_missing.format(field_name=on_field_b))
    else:
        raise Exception(
            geolayer_attributes_missing.format(
                geolayer_name=geolayer_b["metadata"]["name"]
            )
        )


def _name_output_geolayer(output_geolayer_name, geolayer_a_name, geolayer_b_name):

    return output_geolayer_name or "{geolayer_a_name}_join_{geolayer_b_name}".format(
        geolayer_a_name=geolayer_a_name,
        geolayer_b_name=geolayer_b_name,
    )


def _join_create_output_geolayer(
    geolayer_a,
    geolayer_b,
    output_geolayer_name,
    field_name_filter_a,
    field_name_filter_b,
    geometry_ref,
    rename_output_field_from_geolayer_a,
    rename_output_field_from_geolayer_b,
):

    if geometry_ref == "geolayer_a":
        metadata_geometry_ref = "metadata_a"
    elif geometry_ref == "geolayer_b":
        metadata_geometry_ref = "metadata_b"
    else:
        raise Exception(geometry_ref_geolayer)

    # merge geolayer metadata
    merge_metadata_result = merge_metadata(
        metadata_a=geolayer_a["metadata"],
        metadata_b=geolayer_b["metadata"],
        geolayer_name=_name_output_geolayer(
            output_geolayer_name=output_geolayer_name,
            geolayer_a_name=geolayer_a["metadata"]["name"],
            geolayer_b_name=geolayer_b["metadata"]["name"],
        ),
        field_name_filter_a=field_name_filter_a,
        field_name_filter_b=field_name_filter_b,
        geometry_ref=metadata_geometry_ref,
        rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
        rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
    )
    output_metadata = merge_metadata_result["metadata"]
    rename_field_correspondence_a = merge_metadata_result["fields_correspondance_a"]
    rename_field_correspondence_b = merge_metadata_result["fields_correspondance_b"]

    # creating new geolayer
    output_geolayer = {"metadata": output_metadata, "features": {}}

    return (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
    )


def _get_attributes_index(geolayer, field_name_to_index):

    # check if geolayer_join have an attributes index on on_field_join (if not we create it)
    field_index = (
        geolayer["metadata"]
        .get("index", {})
        .get("attributes", {})
        .get(field_name_to_index, None)
    )
    if field_index is None:
        field_index = create_attribute_index(
            geolayer=geolayer, field_name=field_name_to_index
        )

    return field_index


def _prepare_join(
    geolayer_a,
    geolayer_b,
    output_geolayer_name,
    on_field_a,
    on_field_b,
    field_name_filter_a,
    field_name_filter_b,
    rename_output_field_from_geolayer_a,
    rename_output_field_from_geolayer_b,
    geometry_ref,
):
    # check input geolayer
    _check_input_geolayer_data(
        geolayer_a=geolayer_a,
        geolayer_b=geolayer_b,
        on_field_a=on_field_a,
        on_field_b=on_field_b,
    )

    # create output geolayer, output_metadata and rename field correspondence
    (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
    ) = _join_create_output_geolayer(
        geolayer_a=geolayer_a,
        geolayer_b=geolayer_b,
        output_geolayer_name=output_geolayer_name,
        field_name_filter_a=field_name_filter_a,
        field_name_filter_b=field_name_filter_b,
        geometry_ref=geometry_ref,
        rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
        rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
    )

    feature_geometry_ref = "feature_{}"
    if geometry_ref == "geolayer_a":
        feature_geometry_ref = feature_geometry_ref.format("a")
    elif geometry_ref == "geolayer_b":
        feature_geometry_ref = feature_geometry_ref.format("b")
    else:
        raise Exception(geometry_ref_geolayer)

    return (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
        feature_geometry_ref,
    )


def _left_right_join(
    geolayer_left_or_right,
    geolayer_join,
    on_field_left_or_right,
    on_field_join,
    output_metadata,
    field_name_filter_left_or_right,
    field_name_filter_join,
    rename_field_correspondence_left_or_right,
    rename_field_correspondence_join,
    geometry_ref,
    output_geolayer,
):
    # check if geolayer_join have an attributes index on on_field_join (if not we create it)
    on_field_join_index = _get_attributes_index(
        geolayer=geolayer_join, field_name_to_index=on_field_join
    )

    # loop on each feature and make join
    output_geolayer_i_feat = 0
    for i_feat, feature_left_or_right in geolayer_left_or_right["features"].items():
        feature_join_list = []
        if feature_left_right_attributes := feature_left_or_right.get("attributes"):
            # get field value
            on_field_left_right_value = feature_left_right_attributes.get(
                on_field_left_or_right
            )
            if on_field_left_right_value is not None:
                # get join field value
                if on_field_join_i_feat_list := on_field_join_index["index"].get(
                    on_field_left_right_value
                ):
                    for geolayer_join_i_feat in on_field_join_i_feat_list:
                        feature_join_list.append(
                            geolayer_join["features"][geolayer_join_i_feat]
                        )
        # if no feature to join add empty dict
        if not feature_join_list:
            feature_join_list.append({})

        # merge feature_left_or_right with feature_join and add to output_geolayer
        for feature_join in feature_join_list:
            new_feature = merge_feature(
                feature_a=feature_left_or_right,
                feature_b=feature_join,
                merge_metadata=output_metadata,
                field_name_filter_a=field_name_filter_left_or_right,
                field_name_filter_b=field_name_filter_join,
                rename_fields_a=rename_field_correspondence_left_or_right,
                rename_fields_b=rename_field_correspondence_join,
                geometry_ref=geometry_ref,
            )

            output_geolayer["features"][output_geolayer_i_feat] = new_feature
            output_geolayer_i_feat += 1

    return output_geolayer


def join(
    geolayer_a,
    geolayer_b,
    on_field_a,
    on_field_b,
    output_geolayer_name=None,
    field_name_filter_a=None,
    field_name_filter_b=None,
    rename_output_field_from_geolayer_a="auto",
    rename_output_field_from_geolayer_b="auto",
    geometry_ref="geolayer_a",
):
    """
     Make an attributes join between two geolayer.
         - keep only feature with matching on_field_a and on_field_b

       *  *   *  *
     *     *~~*     *
    *  A  *~~~~*  B  *
    *     *~~~~*     *
     *     *~~*     *
        *  *  *  *

     :param geolayer_a: first geolayer to join.
     :param geolayer_b: second geolayer to join.
     :param on_field_a: field of geolayer_a on which we make the join.
     :param on_field_b: field of geolayer_b on which we make the join.
     :param output_geolayer_name: name of new geolayer
     :param field_name_filter_a: field from geolayer_a that we keep.
     :param field_name_filter_b: field from geolayer_b that we keep.
     :param rename_output_field_from_geolayer_a: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param rename_output_field_from_geolayer_b: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param geometry_ref: if there is geometry in geolayer_a and/or geolayer_b from which geolayer geometry is keep ? (
    'geolayer_a' or 'geolayer_b').
     :return: geolayer_a join by geolayer_b
    """
    (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
        feature_geometry_ref,
    ) = _prepare_join(
        geolayer_a,
        geolayer_b,
        output_geolayer_name,
        on_field_a,
        on_field_b,
        field_name_filter_a,
        field_name_filter_b,
        rename_output_field_from_geolayer_a,
        rename_output_field_from_geolayer_b,
        geometry_ref,
    )

    # create index
    on_field_a_index = _get_attributes_index(
        geolayer=geolayer_a, field_name_to_index=on_field_a
    )
    on_field_b_index = _get_attributes_index(
        geolayer=geolayer_b, field_name_to_index=on_field_b
    )

    # get common key value
    common_value_set = set(on_field_a_index["index"].keys()).intersection(
        set(on_field_b_index["index"].keys())
    )
    # delete none value
    common_value_set = common_value_set - {None}
    # get i_feat
    i_feat_list = []
    for common_value in common_value_set:
        for i_feat in on_field_a_index["index"][common_value]:
            i_feat_list.append(i_feat)

    output_geolayer_i_feat = 0
    for i_feat in sorted(i_feat_list):
        feature_a = geolayer_a["features"][i_feat]
        feature_a_field_value = feature_a.get("attributes").get(on_field_a)
        for i_feat_b in sorted(on_field_b_index["index"][feature_a_field_value]):
            feature_b = geolayer_b["features"][i_feat_b]
            new_feature = merge_feature(
                feature_a,
                feature_b,
                merge_metadata=output_metadata,
                field_name_filter_a=field_name_filter_a,
                field_name_filter_b=field_name_filter_b,
                rename_fields_a=rename_field_correspondence_a,
                rename_fields_b=rename_field_correspondence_b,
                geometry_ref=feature_geometry_ref,
            )
            output_geolayer["features"][output_geolayer_i_feat] = new_feature
            output_geolayer_i_feat += 1

    return output_geolayer


def join_full(
    geolayer_a,
    geolayer_b,
    on_field_a,
    on_field_b,
    output_geolayer_name=None,
    field_name_filter_a=None,
    field_name_filter_b=None,
    rename_output_field_from_geolayer_a="auto",
    rename_output_field_from_geolayer_b="auto",
    geometry_ref="geolayer_a",
):
    """
     Make an attributes full join between two geolayer.
     - keep all feature with matching or not on_field_a and on_field_b.
     - If no matching the field from geolayer_a or geolayer_b that not match have None value.

           *~~*   *~~*
         *~~~~~*~~*~~~~~*
        *~~A~~*~~~~*~~B~~*
        *~~~~~*~~~~*~~~~~*
         *~~~~~*~~*~~~~~*
            *~~*  *~~*

     :param geolayer_a: first geolayer to join.
     :param geolayer_b: second geolayer to join.
     :param on_field_a: field of geolayer_a on which we make the join.
     :param on_field_b: field of geolayer_b on which we make the join.
     :param output_geolayer_name: name of new geolayer
     :param field_name_filter_a: field from geolayer_a that we keep.
     :param field_name_filter_b: field from geolayer_b that we keep.
     :param rename_output_field_from_geolayer_a: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param rename_output_field_from_geolayer_b: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param geometry_ref: if there is geometry in geolayer_a and/or geolayer_b from which geolayer geometry is keep ? (
    'geolayer_a' or 'geolayer_b').
     :return: geolayer_a join by geolayer_b
    """

    # create or get attributes index for on_field_a and on_field_b
    delete_index_a = False
    if check_attributes_index(geolayer=geolayer_a, field_name=on_field_a) is False:
        geolayer_a_on_field_index = create_attribute_index(
            geolayer=geolayer_a, field_name=on_field_a
        )
        add_attributes_index(
            geolayer=geolayer_a, field_name=on_field_a, index=geolayer_a_on_field_index
        )
        delete_index_a = True
    else:
        geolayer_a_on_field_index = geolayer_a["metadata"]["index"]["attributes"][
            on_field_a
        ]

    delete_index_b = False
    if check_attributes_index(geolayer=geolayer_b, field_name=on_field_b) is False:
        geolayer_b_on_field_index = create_attribute_index(
            geolayer=geolayer_b, field_name=on_field_b
        )
        add_attributes_index(
            geolayer=geolayer_b, field_name=on_field_b, index=geolayer_b_on_field_index
        )
        delete_index_b = True
    else:
        geolayer_b_on_field_index = geolayer_a["metadata"]["index"]["attributes"][
            on_field_b
        ]

    geolayer_a_on_field_value_set = set(geolayer_a_on_field_index["index"].keys())
    geolayer_b_on_field_value_set = set(geolayer_b_on_field_index["index"].keys())

    # check i_feat for left join only
    value_in_a_not_in_b = geolayer_a_on_field_value_set - geolayer_b_on_field_value_set

    # check i_feat for join only
    value_in_a_and_b = geolayer_a_on_field_value_set.intersection(
        geolayer_b_on_field_value_set
    )

    value_in_b_not_in_a = geolayer_b_on_field_value_set - geolayer_a_on_field_value_set

    # make join between geolayers
    union_geolayer_list = []
    if value_in_a_not_in_b:
        left_join_geolayer = join_left(
            geolayer_a=geolayer_a,
            geolayer_b=geolayer_b,
            on_field_a=on_field_a,
            on_field_b=on_field_b,
            output_geolayer_name=output_geolayer_name,
            field_name_filter_a=field_name_filter_a,
            field_name_filter_b=field_name_filter_b,
            rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
            rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
            geometry_ref=geometry_ref,
        )
        union_geolayer_list.append(left_join_geolayer)

    if (
        value_in_a_and_b
    ):  # and (value_in_a_not_in_b == set() and value_in_b_not_in_a == set()):
        if value_in_a_not_in_b == set() and value_in_b_not_in_a == set():
            join_geolayer = join(
                geolayer_a=geolayer_a,
                geolayer_b=geolayer_b,
                on_field_a=on_field_a,
                on_field_b=on_field_b,
                output_geolayer_name=output_geolayer_name,
                field_name_filter_a=field_name_filter_a,
                field_name_filter_b=field_name_filter_b,
                rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
                rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
                geometry_ref=geometry_ref,
            )
            union_geolayer_list.append(join_geolayer)

            if None in value_in_a_and_b:
                geolayer_a_whith_only_none_i_feat_list = clause_where(
                    geolayer=geolayer_a,
                    field_name=on_field_a,
                    predicate="=",
                    values=None,
                )
                geolayer_a_with_only_none = create_geolayer_from_i_feat_list(
                    geolayer=geolayer_a,
                    i_feat_list=geolayer_a_whith_only_none_i_feat_list,
                )
                geolayer_b_whith_only_none_i_feat_list = clause_where(
                    geolayer=geolayer_b,
                    field_name=on_field_b,
                    predicate="=",
                    values=None,
                )
                geolayer_b_whith_only_none = create_geolayer_from_i_feat_list(
                    geolayer=geolayer_b,
                    i_feat_list=geolayer_b_whith_only_none_i_feat_list,
                )

                geolayer_none_left = join_left(
                    geolayer_a=geolayer_a_with_only_none,
                    geolayer_b=geolayer_b_whith_only_none,
                    on_field_a=on_field_a,
                    on_field_b=on_field_b,
                    output_geolayer_name=output_geolayer_name,
                    field_name_filter_a=field_name_filter_a,
                    field_name_filter_b=field_name_filter_b,
                    rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
                    rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
                    geometry_ref=geometry_ref,
                )
                union_geolayer_list.append(geolayer_none_left)

                geolayer_none_right = join_right(
                    geolayer_a=geolayer_a_with_only_none,
                    geolayer_b=geolayer_b_whith_only_none,
                    on_field_a=on_field_a,
                    on_field_b=on_field_b,
                    output_geolayer_name=output_geolayer_name,
                    field_name_filter_a=field_name_filter_a,
                    field_name_filter_b=field_name_filter_b,
                    rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
                    rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
                    geometry_ref=geometry_ref,
                )
                union_geolayer_list.append(geolayer_none_right)

    if value_in_b_not_in_a:
        right_join_geolayer = join_right(
            geolayer_a=geolayer_a,
            geolayer_b=geolayer_b,
            on_field_a=on_field_a,
            on_field_b=on_field_b,
            output_geolayer_name=output_geolayer_name,
            field_name_filter_a=field_name_filter_a,
            field_name_filter_b=field_name_filter_b,
            rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
            rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
            geometry_ref=geometry_ref,
        )
        union_geolayer_list.append(right_join_geolayer)

    # delete duplicate values

    # union join
    if len(union_geolayer_list) > 1:
        output_geolayer = union_geolayer(
            union_geolayer_list, geolayer_name=output_geolayer_name, serialize=False
        )
    else:
        output_geolayer = union_geolayer_list[0]

    # name output geolayer
    output_geolayer["metadata"]["name"] = _name_output_geolayer(
        output_geolayer_name=output_geolayer_name,
        geolayer_a_name=geolayer_a["metadata"]["name"],
        geolayer_b_name=geolayer_b["metadata"]["name"],
    )

    # delete created index if not exists originally
    if delete_index_a is True:
        delete_attributes_index(geolayer=geolayer_a, field_name=on_field_a)
    if delete_index_b is True:
        delete_attributes_index(geolayer=geolayer_b, field_name=on_field_b)

    return output_geolayer


def join_left(
    geolayer_a,
    geolayer_b,
    on_field_a,
    on_field_b,
    output_geolayer_name=None,
    field_name_filter_a=None,
    field_name_filter_b=None,
    rename_output_field_from_geolayer_a="auto",
    rename_output_field_from_geolayer_b="auto",
    geometry_ref="geolayer_a",
):
    """
     Make an attributes left join between two geolayer.
         - keep all features from geolayer_a and only features from geolayer_b with matching on_field_a and on_field_b

       *~~*   *  *
     *~~~~~*~~*     *
    *~~A~~*~~~~*  B  *
    *~~~~~*~~~~*     *
     *~~~~~*~~*     *
        *~~*  *  *

     :param geolayer_a: first geolayer to join.
     :param geolayer_b: second geolayer to join.
     :param on_field_a: field of geolayer_a on which we make the join.
     :param on_field_b: field of geolayer_b on which we make the join.
     :param output_geolayer_name: name of new geolayer
     :param field_name_filter_a: field from geolayer_a that we keep.
     :param field_name_filter_b: field from geolayer_b that we keep.
     :param rename_output_field_from_geolayer_a: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param rename_output_field_from_geolayer_b: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param geometry_ref: if there is geometry in geolayer_a and/or geolayer_b from which geolayer geometry is keep ? (
    'geolayer_a' or 'geolayer_b').
     :return: geolayer_a join by geolayer_b"""

    (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
        feature_geometry_ref,
    ) = _prepare_join(
        geolayer_a=geolayer_a,
        geolayer_b=geolayer_b,
        output_geolayer_name=output_geolayer_name,
        on_field_a=on_field_a,
        on_field_b=on_field_b,
        field_name_filter_a=field_name_filter_a,
        field_name_filter_b=field_name_filter_b,
        rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
        rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
        geometry_ref=geometry_ref,
    )

    output_geolayer = _left_right_join(
        geolayer_left_or_right=geolayer_a,
        geolayer_join=geolayer_b,
        on_field_left_or_right=on_field_a,
        on_field_join=on_field_b,
        output_metadata=output_metadata,
        field_name_filter_left_or_right=field_name_filter_a,
        field_name_filter_join=field_name_filter_b,
        rename_field_correspondence_left_or_right=rename_field_correspondence_a,
        rename_field_correspondence_join=rename_field_correspondence_b,
        geometry_ref=feature_geometry_ref,
        output_geolayer=output_geolayer,
    )

    return output_geolayer


def join_right(
    geolayer_a,
    geolayer_b,
    on_field_a,
    on_field_b,
    output_geolayer_name=None,
    field_name_filter_a=None,
    field_name_filter_b=None,
    rename_output_field_from_geolayer_a="auto",
    rename_output_field_from_geolayer_b="auto",
    geometry_ref="geolayer_b",
):
    """
     Make an attributes right join between two geolayer.
         - keep all features from geolayer_b and only features from geolayer_a with matching on_field_a and on_field_b

       *  *   *~~*
     *     *~~*~~~~~*
    *  A  *~~~~*~~B~~*
    *     *~~~~*~~~~~*
     *     *~~*~~~~~*
        *  *  *~~*

     :param geolayer_a: first geolayer to join.
     :param geolayer_b: second geolayer to join.
     :param on_field_a: field of geolayer_a on which we make the join.
     :param on_field_b: field of geolayer_b on which we make the join.
     :param output_geolayer_name: name of new geolayer
     :param field_name_filter_a: field from geolayer_a that we keep.
     :param field_name_filter_b: field from geolayer_b that we keep.
     :param rename_output_field_from_geolayer_a: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param rename_output_field_from_geolayer_b: field from geolayer that we want to rename in output geolayer
     (to avoid field with same name between geolayer_a and geolayer_b). By default, the renaming is automatic, but
     you can give a dict with thi pattern :
         {'old_field_name_x': 'new_field_name_x' 'old_field_name_y': 'new_field_name_y'}
     :param geometry_ref: if there is geometry in geolayer_a and/or geolayer_b from which geolayer geometry is keep ? (
    'geolayer_a' or 'geolayer_b').
     :return: geolayer_a join by geolayer_b
    """
    (
        output_geolayer,
        output_metadata,
        rename_field_correspondence_a,
        rename_field_correspondence_b,
        feature_geometry_ref,
    ) = _prepare_join(
        geolayer_a=geolayer_a,
        geolayer_b=geolayer_b,
        output_geolayer_name=output_geolayer_name,
        on_field_a=on_field_a,
        on_field_b=on_field_b,
        field_name_filter_a=field_name_filter_a,
        field_name_filter_b=field_name_filter_b,
        rename_output_field_from_geolayer_a=rename_output_field_from_geolayer_a,
        rename_output_field_from_geolayer_b=rename_output_field_from_geolayer_b,
        geometry_ref=geometry_ref,
    )
    if feature_geometry_ref == "feature_b":
        feature_geometry_ref = "feature_a"
    else:
        feature_geometry_ref = "feature_b"

    output_geolayer = _left_right_join(
        geolayer_left_or_right=geolayer_b,
        geolayer_join=geolayer_a,
        on_field_left_or_right=on_field_b,
        on_field_join=on_field_a,
        output_metadata=output_metadata,
        field_name_filter_left_or_right=field_name_filter_b,
        field_name_filter_join=field_name_filter_a,
        rename_field_correspondence_left_or_right=rename_field_correspondence_b,
        rename_field_correspondence_join=rename_field_correspondence_a,
        geometry_ref=feature_geometry_ref,
        output_geolayer=output_geolayer,
    )

    return output_geolayer
