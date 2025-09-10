from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from geoformat.conf.error_messages import (
    path_not_valid,
    path_not_valid_file_exists_overwrite_is_false,
    path_http_not_valid,
    path_not_http,
    path_not_a_dir,
)


def add_extension_path(path, add_extension):
    """
    Add extension to path if add extension is specified

    :param path: input path
    :param add_extension:
    :return: output path
    """
    if add_extension and add_extension != path.suffix:
        path = path.with_suffix(path.suffix + add_extension)

    return path


def path_is_file(path):
    """
    Test if given path is a file.

    :param path: path to something
    :return: True if path is a path / False if not.
    """
    p = Path(path)
    is_file = False
    if p.is_file():
        is_file = True

    return is_file


def path_is_dir(path):
    """
    Test if given path is a dir.

    :param path: path to something
    :return: True if path is a dir path / False if not.
    """
    p = Path(path)
    is_dir = False
    if p.is_dir():
        is_dir = True

    return is_dir

def path_is_http(path, headers=None):
    """
    Test if given path is a http valid http link.

    :param path: path to something.
    :param headers: optionally you can add headers of http parameters
    :return: True if path is a http path / False if not.
    """
    if headers is None:
        headers = {}
    is_http = False
    resp_code = None
    if str(path).startswith("http"):
        req = Request(path, headers=headers)
        try:
            resp = urlopen(req)
            resp_code = resp.code
            if resp_code == 200:
                is_http = True
        except URLError:
            resp_code = 404

    return is_http, resp_code



def verify_input_path_is_file(path):
    """
    Transform str path to Path object from pathlib if given path exists and is a file
    :param path: str path or pathlib Path object
    :return: Path object or error message if path isn't valid.
    """

    if path_is_file(path) is True:
        p = Path(path)
        return p
    else:
        raise Exception(path_not_valid.format(path=path))

def verify_input_path_is_dir(path):
    """
    Transform str path to Path object from pathlib if given path exists and is a dir
    :param path: str path or pathlib Path object
    :return: Path object
    """
    p = Path(path)
    if p.is_dir():
        return p
    else:
        raise Exception(path_not_a_dir.format(path=path))

def verify_input_path_is_http(path, headers=None):
    """
    Take http path and test it validity. Return http path if it ok.

    :param path: str path or pathlib Path object
    :param headers: Optionally you can add headers of http parameters
    :return: http path if it's ok then error message
    """
    is_http, resp_code = path_is_http(path=path, headers=headers)
    if is_http is True:
        return path
    else:
        if resp_code is None:
            raise Exception(path_not_http.format(path=path))
        else:
            raise Exception(path_http_not_valid.format(path=path, code=resp_code))


def open_http_path(path, headers=None):
    """
    Open a http path and return response.

    :param path: http path
    :param headers: optionally you can add headers of http parameters.
    :return: response of http request
    """
    if headers is None:
        headers = {}
    req = Request(path, headers=headers)
    resp = urlopen(req)

    return resp

def path_to_file_path(path, geolayer_name, overwrite=True, add_extension=None):
    """
    Return verified file path for input path.
    Make difference between path dir and path file and return always

    :param path: dir path or file path to be checked.
    :param geolayer_name: name of geolayer (only used when path is dir path)
    :param overwrite: True we overwrite file if exists, False we return an error if file exists
    :param add_extension: if input path if file (without extension) or dir if add extension is True we add file
    extension specified ('geojson', 'shp', 'kml' ...)
    :return: output path
    """
    p = Path(path)
    file_path = None
    if p.exists() is True:
        # check if is dir
        if p.is_dir() is True:
            file_path = p.joinpath(geolayer_name)
        # chek if it's file
        elif p.is_file():
            file_path = p
    # file or dir does not exist
    else:
        if p.parent.exists():
            file_path = p
        else:
            raise Exception(path_not_valid.format(path=path))

    # add extension
    file_path = add_extension_path(path=file_path, add_extension=add_extension)

    # check overwrite
    if file_path.exists() and overwrite is False:
        raise Exception(
            path_not_valid_file_exists_overwrite_is_false.format(path=file_path)
        )

    return file_path
