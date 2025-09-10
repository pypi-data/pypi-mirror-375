# python version
python_inferior_to_3_7_forbidden = (
    "you must have a version of python higher or equal to 3.7 to execute this function"
)
python_inferior_to_3_8_forbidden = (
    "you must have a version of python higher or equal to 3.8 to execute this function"
)

# driver
import_lib_error = "cannot run this function ! {lib} library not installed"
import_ogr_error = import_lib_error.format(lib="Python-gdal")
import_psycopg2_error = import_lib_error.format(lib="psycopg2")
import_pyproj_error = import_lib_error.format(lib="pyproj")
import_shapefile_error = import_lib_error.format(lib="shapefile")
import_matplotlib_error = import_lib_error.format(lib="matplotlib")
import_numpy_error = import_lib_error.format(lib="numpy")

key_parameter_invalid = "key : {key} not supported"


# path
path_not_valid = "path : {path} is not valid"
path_not_a_dir = f"{path_not_valid}, it must be a directory"
path_not_a_file = f"{path_not_valid}, it must be a file"
path_not_valid_file_exists_overwrite_is_false = "path : {path} exists."
path_http_not_valid = "{path} not valid, code : {code}"
path_not_http = "{path} is not http path"
path_not_exists = "cannot load data file or http address does not exists"

# fields
field_missing = "field : {field_name} does not exists."
field_exists = "{field_name} still exists"
field_type_not_valid = "field type {field_type} not valid. You must use a type in this list : {field_type_list}"
field_width_not_valid = "width value for field {field_name} must be specified"
field_precision_not_valid = "precision value for field {field_name} must be specified"
field_name_length_not_valid = "the maximum number of characters possible for a field (defined by the variable {variable_name}) does not allow to create a unique field."

# geolayer
geolayer_attributes_missing = "there is no attributes data in {geolayer_name} geolayer"

# values

# non unique value
non_unique_values = "field : {field_name} contains non-unique values"

# geometry format
geometry_format_not_exists = (
    "geometry format does not exists you must choose between GEOJSON, WKB or WKT format"
)
geometry_type_not_allowed = "geometry type : {geometry_type} not allowed"
geometry_type_does_not_allowed_in_geolayer = geometry_type_not_allowed + "in geolayer"
geometry_must_be_polygon_or_multipolygon = 'geometry must be POLYGON or MULTIPOLYGON'

# metadata
metadata_fields_not_same = "metadata fields must be identical"
metadata_geometry_ref_not_found = "there is no geometry referenced in metadata"
metadata_geometry_ref_type_not_match = "geometry type is not compatible with metadata"
metadata_geometry_crs = "crs must be identical"

# variable
variable_wrong_formatting = (
    "variable {variable_name} not well formatted please refer to the doc"
)
variable_input_value_error = "variable {variable_name} input error (see doc)"
variable_must_be_int = "variable {variable_name} must be in int"
variable_must_be_fill = 'variable {variable_name} must be fill'

# join
geometry_ref_geolayer = "geometry_ref value must be 'geolayer_a' or 'geolayer_b'"
geometry_ref_metadata = "geometry_ref value must be 'metadata_a' or 'metadata_b'"
geometry_ref_feature = "geometry_ref value must be 'feature_a' or 'feature_b'"

# index
field_name_not_indexing = "field name : {field_name} not indexing the index type is not the one you are looking for"
field_name_still_indexing = "{field_name} is still indexing"
# date to str format
date_format_error = "value must one/or a list of this key 'year' 'month' 'day'  'hour' 'second' 'microsecond'"

# geometry type
geometry_not_in_variable = "{geometry_type} must be include in {variable_name}"
key_use_only_by_geometry = "{key} can only be used on {geometry_type} type"

# Others
field_width_float_not_none = "field_width_float cannot be None if field_type is 'Float'"
variables_must_be_true = "At least one of this variables ({variables}) must be True"

# feature / i_feat
feature_missing = "feature : {i_feat} does not exists"