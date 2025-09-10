import copy
from typing import Union, List, Any

from geoformat.geoprocessing.measure.mesure_area import triangle_area
from geoformat.geoprocessing.connectors.operations import (
    coordinates_to_point
)

from geoformat.geoprocessing.geoparameters.boundaries import ccw_or_cw_boundary

from geoformat.conf.error_messages import import_pyproj_error

try:
    from pyproj import Transformer
    import_pyproj_success = True
except ImportError:
    import_pyproj_success = False


def format_coordinates(
        coordinates_list_tuple,
        format_to_type=list,
        precision=None,
        delete_duplicate_following_coordinates=False,
        delete_vertex_list=None,
        delete_collinear_vertex=False,
        in_crs=None,
        out_crs=None,
        translate=None,
):
    """
    This function allow to :
        - reproject coordinates to in_crs to another out_crs
        - round coordinates
        - delete duplicate following coordinates in
        - change type of coordinate's storage

    :param coordinates_list_tuple: tuple or list containing coordinates
    :param format_to_type:  storage data type (list (by default) or tuple)
    :param precision: desired number of decimal for coordinates
    :param delete_duplicate_following_coordinates: option to delete similar coordinates that follow each other
    :param delete_vertex_list: delete vertex if exists in coordinates - list of vertex
    :param delete_collinear_vertex: delete collinear vertex in coordinates
    :param in_crs: input coordinates EPSG.
    :param out_crs: output coordinates EPSG wanted.
    :param out_crs: output coordinates EPSG wanted.
    :param translate: if you want to translate coordinates on x or y axis. example (-1, 1) it will move coordinates
        to -1 on x and +1 on y.
    :return: formatted coordinates
    """

    # format delete_vertex_list
    if delete_vertex_list is not None:
        if isinstance(delete_vertex_list[0], tuple):
            delete_vertex_list = format_coordinates(coordinates_list_tuple=delete_vertex_list, format_to_type=list)
    if import_pyproj_success is True:
        # TODO add delete duplicated part
        if coordinates_list_tuple:
            output_coordinates_list_tuple = copy.deepcopy(coordinates_list_tuple)
            point_list = False
            if isinstance(output_coordinates_list_tuple[0], (float, int)):
                point_list = True
                output_coordinates_list_tuple = [output_coordinates_list_tuple]

            if isinstance(output_coordinates_list_tuple[0][0], (int, float)):
                # reproject if necessary
                if in_crs is not None and out_crs is not None:
                    x_coords, y_coords = zip(*output_coordinates_list_tuple)
                    transformer = Transformer.from_crs(f"EPSG:{in_crs}", f"EPSG:{out_crs}", always_xy=True)
                    transform_coords = transformer.transform(x_coords, y_coords)
                    output_coordinates_list_tuple = zip(*transform_coords)

                if precision is not None:
                    # change precision
                    output_coordinates_list_tuple = [[round(xyz, precision) for xyz in coordinates] for coordinates in
                                                     output_coordinates_list_tuple]

                if translate is not None:
                    output_coordinates_list_tuple = [[xyz + translate[i] for i, xyz in enumerate(coordinates)] for coordinates in
                                                     output_coordinates_list_tuple]
                # FORMAT coordinates storage type
                # reformat coordinates storage type (list or tuple)
                if format_to_type:
                    output_coordinates_list_tuple = format_to_type(
                        [format_to_type(coordinates) for coordinates in output_coordinates_list_tuple])
            else:

                output_coordinates_list_tuple = [None] * len(coordinates_list_tuple)
                # here we first format type of storage of coordinates and precision
                for i_coord, coordinates in enumerate(coordinates_list_tuple):
                    coord_tuple = format_coordinates(
                        coordinates_list_tuple=coordinates,
                        format_to_type=format_to_type,
                        precision=precision,
                        delete_duplicate_following_coordinates=delete_duplicate_following_coordinates,
                        delete_vertex_list=delete_vertex_list,
                        delete_collinear_vertex=delete_collinear_vertex,
                        in_crs=in_crs,
                        out_crs=out_crs,
                        translate=translate,
                    )
                    output_coordinates_list_tuple[i_coord] = coord_tuple

                if format_to_type:
                    output_coordinates_list_tuple = format_to_type(output_coordinates_list_tuple)

            # reformat coordinates list to point
            if point_list is True:
                output_coordinates_list_tuple = output_coordinates_list_tuple[0]

            # DELETE COORDINATES OR DUPLICATE FOLLOWING COORDINATES
            # in step before if we reformat precision we can create duplicate coordinates then if
            # delete_duplicate_following_coordinates is True we have to make a second scan of coordinates
            # if we are at level of part of geometry (list that contains coordinates in it)
            if (
                    (
                            delete_duplicate_following_coordinates is True
                            or delete_collinear_vertex is True
                            or (
                                    delete_vertex_list is not None
                                    and isinstance(output_coordinates_list_tuple, (list, tuple))
                                    and len(output_coordinates_list_tuple) > 0
                                    and isinstance(output_coordinates_list_tuple[0], (list, tuple))
                                    and len(output_coordinates_list_tuple[0]) > 0
                                    and isinstance(output_coordinates_list_tuple[0][0], (int, float))
                            )
                    )
            ):
                if delete_collinear_vertex is True:
                    # in this case we delete duplicate following coordinates first to avoid mix of duplicate and
                    # collinear point at same time. So fist we delete duplicate then we found collinear and delete them
                    output_coordinates_list_tuple = format_coordinates(
                        coordinates_list_tuple=output_coordinates_list_tuple,
                        delete_duplicate_following_coordinates=True,
                    )
                # scan list of coordinates or list of coordinates (don't scan coordinate list)
                # if coordinates
                retype_to_tuple = False
                # transform tuple to list (because we need to edit coordinates)
                if isinstance(output_coordinates_list_tuple, tuple):
                    retype_to_tuple = True
                    output_coordinates_list_tuple = list(output_coordinates_list_tuple)

                # try to find duplicate coordinates index
                coordinates_to_delete_idx_list = []
                for idx_inside_coord, inside_coordinates in enumerate(output_coordinates_list_tuple):
                    delete_coordinate = False # init delete vertex variable
                    if idx_inside_coord == 0:
                        coordinates_to_delete_idx_list = []
                    else:
                        if delete_duplicate_following_coordinates is True:
                            # if coordinates are same that previous index of coordinates is save in
                            # duplicate_coordinates_idx_list (we delete this coordinates after the loop)
                            if previous_coordinates == inside_coordinates:
                                delete_coordinate = True
                        if delete_collinear_vertex is True and delete_coordinate is False:
                            if 0 < idx_inside_coord < len(output_coordinates_list_tuple) - 1:
                                next_coordinates = output_coordinates_list_tuple[idx_inside_coord+1]
                                if triangle_area(previous_coordinates, inside_coordinates, next_coordinates) == 0:
                                    delete_coordinate = True

                    # delete coordinates if wanted
                    if delete_vertex_list and delete_coordinate is False:
                        if inside_coordinates in delete_vertex_list:
                            delete_coordinate = True

                    if delete_coordinate is True:
                        coordinates_to_delete_idx_list.append(idx_inside_coord)

                    previous_coordinates = inside_coordinates

                # delete vertex
                if coordinates_to_delete_idx_list:
                    for idx in reversed(coordinates_to_delete_idx_list):
                        del output_coordinates_list_tuple[idx]

                # retype to tuple if output_coordinates_list_tuple is originally a tuple
                if retype_to_tuple is True:
                    output_coordinates_list_tuple = tuple(output_coordinates_list_tuple)
        else:
            if format_to_type == list:
                output_coordinates_list_tuple = []
            else:
                output_coordinates_list_tuple = ()

    else:
        raise Exception(import_pyproj_error)

    return output_coordinates_list_tuple


def coordinates_to_2d_coordinates(coordinates_list):
    """
    Convert a coordinates list with x dimension to 2d dimension list

    :param coordinates_list: list of coordinates with 2 or more dimension
    :return: coordinates list with only 2 dimensions.
    """

    if coordinates_list:
        if isinstance(coordinates_list[0], (int, float)):
            new_coordinates = [coordinates_list[0], coordinates_list[1]]
        elif isinstance(coordinates_list[0], (tuple, list)):
            new_coordinates = [None] * len(coordinates_list)
            for i_coord, under_coordinates in enumerate(coordinates_list):
                new_coordinates[i_coord] = coordinates_to_2d_coordinates(under_coordinates)
        else:
            raise Exception('error your geometry in input is not correct')
    else:
        new_coordinates = []

    return new_coordinates


def coordinates_to_centroid(coordinates_list_tuple, precision=None):
    """
    Return the centroid of given coordinates list or tuple

    :param coordinates_list_tuple: (list or tuple) coordinates list or tuple
    :param precision: (int) precision of coordinates (number of decimal places)
    :return: (tuple) centroid
    """

    for i_point, point in enumerate(coordinates_to_point(coordinates_list_tuple)):
        if i_point == 0:
            mean_point = list(point)
        else:
            mean_point[0] += point[0]
            mean_point[1] += point[1]

    nb_coordinates = i_point + 1
    centroid = [mean_point[0] / nb_coordinates, mean_point[1] / nb_coordinates]

    if precision:
        centroid = format_coordinates(coordinates_list_tuple=centroid, precision=precision)

    return centroid


def separate_coordinates_dimensions(
    coordinates: Union[List[Union[float, List[Any]]], tuple]
) -> List[List[List[Union[float, int]]]]:
    """
    Separates the coordinates dimensions of coordinates into distinct lists while preserving
    the original structure and depth of the input data.

    This function supports coordinates in point, line, polygon, and multipolygon formats,
    including those with an arbitrary number of dimensions (e.g., x, y, z).

    Parameters:
    ----------
    coordinates : Union[List[Union[float, List[Any]]], tuple]
        A list or tuple of coordinates. Each coordinate can be a number (for a point),
        a list of numbers (for a line or polygon), or a list of lists of numbers
        (for a polygon with holes or a multipolygon).

    Returns:
    -------
    List[List[List[Union[float, None]]]]
        A list of lists of lists where each top-level list represents one dimension
        of the coordinates (e.g., all x's, all y's, etc.), with the original nesting
        structure preserved.

    """
    # Converts coordinates to a list if not already, to standardize processing.
    if not isinstance(coordinates[0], (tuple, list)):
        coordinates = [coordinates]

    # Initializes the structure that will contain the final result.
    result_structure = [[None] for _ in range(len(coordinates))]
    separated_dimensions = None

    for index, coord_group in enumerate(coordinates):
        if isinstance(coord_group[0], (tuple, list)):
            # If the coordinate group is itself a list, process it recursively.
            nested_dimensions = separate_coordinates_dimensions(coord_group)
            if not separated_dimensions:
                separated_dimensions = [
                    [list(subgroup) for subgroup in result_structure]
                    for _ in range(len(nested_dimensions))
                ]
            for dim_index, nested_coord in enumerate(nested_dimensions):
                separated_dimensions[dim_index][index] = nested_coord
        else:
            # For a linear coordinate group (no sub-lists), separate the dimensions directly.
            if not separated_dimensions:
                separated_dimensions = [
                    [list(subgroup) for subgroup in result_structure]
                    for _ in range(len(coord_group))
                ]
            for dim_index, value in enumerate(coord_group):
                separated_dimensions[dim_index][index][0] = value

    return separated_dimensions

def force_rhr_polygon_coordinates(coordinates):
    output_ring = [None] * len(coordinates)
    # loop on each ring
    for i_ring, ring_coordinates in enumerate(coordinates):
        ring_direction = ccw_or_cw_boundary(ring_coordinates)
        # for exterior ring
        if i_ring == 0:
            # if counter clock wise we reverse ring's coordinates
            if ring_direction == 'CCW':
                ring_coordinates.reverse()
        # for interrior ring
        else:
            # if clock wise we reverse ring's coordinates
            if ring_direction == 'CW':
                ring_coordinates.reverse()
        # saving ring
        output_ring[i_ring] = ring_coordinates

    return output_ring