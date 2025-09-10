import copy

from geoformat.conf.error_messages import (
    field_missing,
    field_exists,
    field_type_not_valid,
    field_width_not_valid,
    field_precision_not_valid,
    variable_must_be_int,
    field_name_not_indexing,
    field_name_still_indexing,
)

from geoformat.conf.fields_variable import (
    field_metadata_width_required,
    field_metadata_precision_required,
    field_type_set,
)

from geoformat.conf.format_data import value_to_iterable_value


def drop_field_in_metadata(metadata, field_name_or_field_name_list):
    """
    Drop field(s) in metadata contains in field_name_or_field_name_list

    :param metadata:
    :param field_name_or_field_name_list:
    :return: metadata without deleted field
    """
    field_name_or_field_name_list = value_to_iterable_value(
        field_name_or_field_name_list, output_iterable_type=list
    )
    reorder_field_index = []
    if "fields" in metadata:
        output_metadata = copy.deepcopy(metadata)
        for field_name in field_name_or_field_name_list:
            if field_name in metadata["fields"]:
                if "index" in metadata["fields"][field_name]:
                    reorder_field_index.append(metadata["fields"][field_name]["index"])
                del output_metadata["fields"][field_name]

        # reorder field index
        if reorder_field_index:
            output_metadata["fields"] = reorder_metadata_field_index_after_field_drop(
                fields_metadata=output_metadata["fields"],
                reorder_field_index=reorder_field_index,
            )

        # if there is no field in metadata we delete fields key in it
        if len(output_metadata["fields"]) == 0:
            del output_metadata["fields"]
    else:
        output_metadata = metadata

    return output_metadata


def drop_field_that_not_exists_in_metadata(
    metadata,
    not_deleting_field_name_or_field_name_list
):
    """
    Drop field that not exists in metadata

    :param metadata: metadata with the fields you want to keep.
    :param not_deleting_field_name_or_field_name_list: field name (or field name list) that you want to keep
    :return: metadata without field
    """
    if metadata["fields"]:
        field_to_delete_list = []
        for field_name in metadata["fields"]:
            if field_name not in not_deleting_field_name_or_field_name_list:
                field_to_delete_list.append(field_name)

        if field_to_delete_list:
            metadata = drop_field_in_metadata(
                metadata=metadata, field_name_or_field_name_list=field_to_delete_list)

    return metadata


def reorder_metadata_field_index_after_field_drop(fields_metadata, reorder_field_index):
    """
    This function is used when a field is deleted in a geolayer.

    Reorder "index" key in fields_metadata for step(s) specified in reorder_field_index.

    :param fields_metadata: field metadata from geolayer
    :param reorder_field_index: list that contains original index to delete field.
    :return: fields_metadata with field index reordered after field delete
    """

    # init reorder field index
    reorder_field_index = value_to_iterable_value(reorder_field_index, list)

    # sort index
    reorder_field_index.sort()
    # loop on each index
    for idx in reversed(reorder_field_index):
        for field_name, field_metadata in fields_metadata.items():
            if field_metadata["index"] > idx:
                field_metadata["index"] = field_metadata["index"] - 1

    return fields_metadata


def rename_field_in_metadata(metadata, old_field_name, new_field_name):
    """
    Rename field in metadata

    :param old_field_name: current name of the field you want to modify.
    :param new_field_name: new name to the field that we want change.
    :return: metadata with rename field name.
    """
    output_metadata = copy.deepcopy(metadata)
    if geolayer_fields_metadata := output_metadata.get("fields", {}):
        if old_field_name in geolayer_fields_metadata:
            if new_field_name not in geolayer_fields_metadata:
                # rename in geolayer metadata
                geolayer_fields_metadata[new_field_name] = dict(
                    geolayer_fields_metadata[old_field_name]
                )
                del geolayer_fields_metadata[old_field_name]
            else:
                raise Exception(field_exists.format(field_name=new_field_name))
        else:
            raise Exception(field_missing.format(field_name=old_field_name))

    return output_metadata


def create_field_in_metadata(
    metadata, field_name, field_type, field_width, field_precision
):
    """
    Add a field in metadata

    :param field_name: new field name to create
    :param field_type: field type for new field
    :param field_width: field width for new field
    :param field_precision: field precision for new field
    :return: input metadata with new field in it
    """

    # check if field not exists
    if metadata_fields := metadata.get("fields"):
        if field_name in metadata_fields:
            raise Exception(field_exists.format(field_name=field_name))
    else:
        metadata["fields"] = {}

    # check field_type
    if field_type not in field_type_set:
        raise Exception(
            field_type_not_valid.format(
                field_type=field_type, field_type_list=sorted(list(field_type_set))
            )
        )

    # check field_width
    if field_type in field_metadata_width_required:
        if field_width is None:
            raise Exception(field_width_not_valid.format(field_name=field_name))
        else:
            if not isinstance(field_width, int):
                raise Exception(
                    variable_must_be_int.format(variable_name="field_width")
                )
    else:
        field_width = None

    # check field_precision
    if field_type in field_metadata_precision_required:
        if field_precision is None:
            raise Exception(field_precision_not_valid.format(field_name=field_name))
        else:
            if not isinstance(field_precision, int):
                raise Exception(
                    variable_must_be_int.format(variable_name="field_precision")
                )
    else:
        field_precision = None

    metadata["fields"][field_name] = {"type": field_type}

    if field_width:
        metadata["fields"][field_name]["width"] = field_width

    if field_precision:
        metadata["fields"][field_name]["precision"] = field_precision

    # add index
    metadata["fields"][field_name]["index"] = len(metadata["fields"]) - 1

    return metadata


def check_if_field_exists_in_metadata(metadata, field_name):
    """
    Check if field exists in given metadata.

    :param metadata: input metadata where existing field name is tested.
    :param field_name: name of field.
    :return: True if field exists False if not.
    """

    return_value = False
    if metadata.get("fields"):
        if metadata["fields"].get(field_name):
            return_value = True

    return return_value


def check_attributes_index_in_metadata(metadata, field_name, type=None):
    """
    Return True or False if an attributes index is found in metadata for input field_name optionaly we can test
    type index

    :param metadata: input metadata
    :param field_name: field name where is the index
    :param type: type of indexing (hashtable/btree ...)
    :return: Boolean
    """
    found_index = False
    if check_if_field_exists_in_metadata(metadata=metadata, field_name=field_name):
        if "index" in metadata:
            if "attributes" in metadata["index"]:
                if field_name in metadata["index"]["attributes"]:
                    found_index = True
                    if type:
                        if metadata["index"]["attributes"][field_name]['metadata']["type"] != type:
                            found_index = False
    else:
        raise Exception(field_missing.format(field_name=field_name))

    return found_index


def add_attributes_index_in_metadata(metadata, field_name, index):
    """Store index in metadata

    :param metadata: metadata to add an attributes
    :field_name: name of field concern by index
    :index: index that we want to add to field of geolayer
    :return: geolayer with index in it
    """

    # check if field_name exists
    if (
        check_if_field_exists_in_metadata(metadata=metadata, field_name=field_name)
        is False
    ):
        raise Exception(field_missing.format(field_name=field_name))

    # create index structure in metadata (if not)
    metadata_index = metadata.get("index")
    if metadata_index is None:
        metadata["index"] = {}
        metadata_index = metadata["index"]

    metadata_index_attributes = metadata_index.get("attributes")
    if metadata_index_attributes is None:
        metadata_index["attributes"] = {}
        metadata_index_attributes = metadata_index["attributes"]

    # check if index is yet in store in geolayer
    if metadata_index_attributes.get(field_name):
        raise Exception(field_name_still_indexing.format(field_name=field_name))

    metadata_index_attributes[field_name] = index

    return metadata


def delete_attributes_index_in_metadata(metadata, field_name, type):
    """Delete attributes index when existing in metadata. Opionnaly you can filter on index type.

    :param metadata: input metadata
    :param field_name: field name where is the index
    :param type: type of indexing (hashtable/btree ...)
    :return: Geolayer without index for given field_name (and optionally index type)
    """

    if check_attributes_index_in_metadata(metadata, field_name, type) is True:
        del metadata["index"]["attributes"][field_name]
        if len(metadata["index"]["attributes"]) == 0:
            del metadata["index"]["attributes"]
        if len(metadata["index"]) == 0:
            del metadata["index"]
    else:
        raise Exception(field_name_not_indexing.format(field_name=field_name))

    return metadata
