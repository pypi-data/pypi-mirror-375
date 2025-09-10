from importlib.metadata import (
    version as lib_version,
    PackageNotFoundError,
)

def get_version():
    package_name = 'geoformat'
    try:
        return lib_version(package_name)
    except PackageNotFoundError:
        return "unknown version"

__version__ = get_version()