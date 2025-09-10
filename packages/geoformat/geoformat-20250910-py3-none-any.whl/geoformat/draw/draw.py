from typing import Dict, List, Tuple

from geoformat.conf.error_messages import import_matplotlib_error, import_numpy_error
from geoformat.conversion.coordinates_conversion import force_rhr_polygon_coordinates
from geoformat.conversion.geometry_conversion import geometry_to_bbox
from geoformat.geoprocessing.merge_geometries import merge_geometries

try:
    import numpy as np
    import_numpy_success = True
except ImportError:
    import_numpy_success = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    import_matplotlib_success = True
except ImportError:
    import_matplotlib_success = False


if import_matplotlib_success is True and import_numpy_success is True:
    class DrawGeometry:


        # GEOMETRY DEFAULT STYLE

        # color
        # linewidth
        # linestyle
        # edgecolor
        # facecolor

        VERTEX_MARKER = 'x'
        VERTEX_MARKER_SIZE = 6

        GRATICULE_MAJOR_COLOR = "black"
        GRATICULE_MAJOR_LINE_STYLE = "-"
        GRATICULE_MAJOR_LINE_WIDTH = 0.5
        GRATICULE_MAJOR_ALPHA=0.5
        GRATICULE_MINOR_COLOR = "grey"
        GRATICULE_MINOR_LINE_STYLE = ":"
        GRATICULE_MINOR_LINE_WIDTH = 0.2
        GRATICULE_MINOR_ALPHA=0.5


        def __init__(self, geometry: Dict, *, show_vertices: bool = False) -> None:
            """
            Initializes the DrawGeometry class with geometry data.

            :param geometry: A dictionary representing the geometric data to plot.
            :param show_vertices: If True, draw all vertices of the geometry as points.
            """
            self.geometry = geometry
            self.bbox = geometry.get("bbox") or geometry_to_bbox(geometry=self.geometry)
            self.fig, self.ax = plt.subplots()
            self.show_vertices = show_vertices

        def create_codes(self, num_points: int) -> List[int]:
            """Creates a list of Path codes for constructing a geometry path."""
            return [Path.MOVETO] + [Path.LINETO] * (num_points - 1)

        def validate_coordinates(self, coordinates: List[List[float]]) -> bool:
            """Validates the provided coordinates to ensure they are non-empty and plottable."""
            if coordinates:
                if isinstance(coordinates[0], (list, tuple)):
                    return any(coords for coords in coordinates)
                return True
            return False

        def _plot_vertices(self, points: List[List[float]]) -> None:
            """
            Plot a list of [x, y] points as vertices.
            """
            if not points:
                return
            arr = np.array(points)
            self.ax.plot(arr[:, 0], arr[:, 1], marker=self.VERTEX_MARKER, markersize=self.VERTEX_MARKER_SIZE, color="black", linestyle="None", zorder=3)

        def plot_point(self, coordinates: List[float]) -> None:
            """Plots a single Point geometry."""
            self.ax.plot(coordinates[0], coordinates[1], marker=self.VERTEX_MARKER, markersize=self.VERTEX_MARKER_SIZE, color="black", linestyle="None", zorder=2)
            if self.show_vertices:
                self._plot_vertices([coordinates])

        def plot_line_string(self, coordinates: List[List[float]]) -> None:
            """Plots a single LineString geometry."""
            verts = np.array(coordinates)
            path = Path(verts)
            patch = PathPatch(path, edgecolor='black', facecolor="none", linewidth=1, linestyle='-', zorder=1)
            self.ax.add_patch(patch)
            if self.show_vertices:
                self._plot_vertices(coordinates)

        def plot_polygon(self, coordinates: List[List[List[float]]]) -> None:
            """Plots a Polygon geometry."""
            coordinates = force_rhr_polygon_coordinates(coordinates=coordinates)
            verts = None
            codes = []
            for ring in coordinates:
                ring_verts = np.array(ring)
                if verts is None:
                    verts = ring_verts
                else:
                    verts = np.concatenate([verts, ring_verts])
                codes += self.create_codes(len(ring))
            path = Path(verts, codes)
            patch = PathPatch(path, edgecolor='black', facecolor="#d8e0ea", linewidth=1, linestyle='-', zorder=0)
            self.ax.add_patch(patch)
            if self.show_vertices:
                for ring in coordinates:
                    self._plot_vertices(ring)

        def plot_multi_point(self, coordinates: List[List[float]]) -> None:
            """Plots a MultiPoint geometry."""
            arr = np.array(coordinates)
            self.ax.plot(arr[:, 0], arr[:, 1], marker="o", markersize=10, color="black", linestyle="None", zorder=2)
            if self.show_vertices:
                self._plot_vertices(coordinates)

        def plot_multi_line_string(self, coordinates: List[List[List[float]]]) -> None:
            """Plots a MultiLineString geometry."""
            for ls in coordinates:
                if ls:
                    self.plot_line_string(ls)

        def plot_multi_polygon(self, coordinates: List[List[List[List[float]]]]) -> None:
            """Plots a MultiPolygon geometry."""
            for poly in coordinates:
                if poly:
                    self.plot_polygon(poly)

        def plot_geometry(self, geometry: Dict) -> None:
            """Dispatch to the appropriate plot method based on geometry type."""
            geometry_type = geometry['type']
            geometry_handlers = {
                'Point': self.plot_point,
                'MultiPoint': self.plot_multi_point,
                'LineString': self.plot_line_string,
                'MultiLineString': self.plot_multi_line_string,
                'Polygon': self.plot_polygon,
                'MultiPolygon': self.plot_multi_polygon
            }
            if geometry_type in geometry_handlers:
                handler = geometry_handlers[geometry_type]
                coordinates = geometry.get('coordinates', [])
                if self.validate_coordinates(coordinates=coordinates) is True:
                    handler(coordinates=coordinates)

        def expand_bbox(self) -> Tuple[float, float, float, float]:
            """Expands the bounding box by a margin."""
            if self.bbox:
                x_diff = self.bbox[2] - self.bbox[0]
                y_diff = self.bbox[3] - self.bbox[1]
                x_margin = x_diff * 0.1 or 1
                y_margin = y_diff * 0.1 or 1
                expand_bbox = (
                    self.bbox[0] - x_margin,
                    self.bbox[1] - y_margin,
                    self.bbox[2] + x_margin,
                    self.bbox[3] + y_margin,
                )
            else:
                expand_bbox = (-1, -1, 1, 1)
            return expand_bbox

        def plot(self, graticule: bool = False) -> None:
            """
            Main method to plot the provided geometry.
            """
            if self.geometry['type'] == 'GeometryCollection':
                for geometry in self.geometry['geometries']:
                    self.plot_geometry(geometry)
            else:
                self.plot_geometry(self.geometry)
            margin = self.expand_bbox()
            self.ax.set_xlim(margin[0], margin[2])
            self.ax.set_ylim(margin[1], margin[3])
            if graticule is True:
                self.ax.minorticks_on()
                self.ax.grid(which='major', color=self.GRATICULE_MAJOR_COLOR, linestyle=self.GRATICULE_MAJOR_LINE_STYLE, linewidth=self.GRATICULE_MAJOR_LINE_WIDTH, alpha=self.GRATICULE_MAJOR_ALPHA)
                self.ax.grid(which='minor', color=self.GRATICULE_MINOR_COLOR, linestyle=self.GRATICULE_MINOR_LINE_STYLE, linewidth=self.GRATICULE_MINOR_LINE_WIDTH, alpha=self.GRATICULE_MINOR_ALPHA)
            plt.gca().set_aspect('equal', adjustable='box')
            plt.show()


def draw_geometry(geometry: Dict, graticule: bool = False, *, show_vertices: bool = False) -> None:
    """Wrapper to draw a geometry."""
    if import_matplotlib_success and import_numpy_success:
        DrawGeometry(geometry=geometry, show_vertices=show_vertices).plot(graticule=graticule)
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)


def draw_feature(feature: Dict, graticule: bool = False, *, show_vertices: bool = False) -> None:
    """Wrapper to draw a feature."""
    if import_matplotlib_success and import_numpy_success:
        feature_geometry = feature.get("geometry")
        if feature_geometry:
            draw_geometry(geometry=feature_geometry, graticule=graticule, show_vertices=show_vertices)
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)


def draw_geolayer(geolayer: Dict, graticule: bool = False, *, show_vertices: bool = False) -> None:
    """Wrapper to draw a geolayer."""
    if import_matplotlib_success and import_numpy_success:
        geolayer_geometry = None
        for _, feature in geolayer["features"].items():
            feature_geometry = feature.get('geometry')
            if feature_geometry:
                if geolayer_geometry is None:
                    geolayer_geometry = feature_geometry
                else:
                    geolayer_geometry = merge_geometries(geolayer_geometry, feature_geometry)
        draw_geometry(geometry=geolayer_geometry, graticule=graticule, show_vertices=show_vertices)
    else:
        if not import_matplotlib_success:
            raise Exception(import_matplotlib_error)
        if not import_numpy_success:
            raise Exception(import_numpy_error)
