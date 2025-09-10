import tempfile
from pathlib import Path

from geoformat.conf.path import (
    verify_input_path_is_file,
    verify_input_path_is_http,
    path_is_file,
    path_is_http,
    open_http_path,
)

from geoformat.conf.error_messages import path_not_exists

def _get_recast_field_type_mapping(fields_metadata, geoformat_type_to_output_driver_type):
    """
    From geolayer field's metadata to output driver recast dict

    :param fields_metadata: geolayer field's metadata
    :param geoformat_type_to_output_driver_type: dict that make translation between geoformat type and output driver
    type

    :return: dict that allow to recast field
    """
    recast_field_mapping = {}
    if fields_metadata:
        for field_name, field_metadata in fields_metadata.items():
            recast_to_python_type = geoformat_type_to_output_driver_type.get(field_metadata['type'], None)
            if recast_to_python_type is not None:
                recast_field_mapping[field_name] = {
                    "recast_value_to_python_type": recast_to_python_type,
                    "resize_value_width": None,
                    "resize_value_precision": None
                }

    return recast_field_mapping


def load_data(path, encoding='utf8', http_headers=None, read_mode='r',  temp_mode='w',):
    """
    From path return data as a NamedTemporaryFile object

    :param path: file path or http path
    :param encoding: specify file char encoding (default value utf8)
    :param http_headers: optionally you can add headers of http parameters
    :param read_mode: data is open in 'r' mode (by default) but you can choose an other parameters ('rb', 'r+b')
    :param temp_mode: data is load in NamedTemporaryFile we can choose writing mode
    :return:
    """
    # create temporary file
    fp = tempfile.NamedTemporaryFile(mode=temp_mode)

    if path_is_file(path=path) is True:
        p = verify_input_path_is_file(path=path)
        # open file
        with open(file=p, mode=read_mode, encoding=encoding) as file:
            fp.write(file.read())

    elif path_is_http(path=path, headers=http_headers)[0] is True:
        p = verify_input_path_is_http(path=path, headers=http_headers)
        http_req = open_http_path(path=p, headers=http_headers)
        http_req_str = http_req.read()
        if encoding is not None:
            http_req_str = http_req_str.decode(encoding)
        fp.write(http_req_str)
        file_name = http_req.info().get_filename()
        if file_name is None:
            file_name = path.split('/')[-1]
        p = Path(file_name)
    else:
        raise Exception(path_not_exists)

    fp.seek(0)

    file_name = p.stem
    return fp, file_name
