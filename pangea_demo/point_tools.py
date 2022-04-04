import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Union
from PIL import Image, ImageDraw
import logging
import numpy as np

logger = logging.getLogger()


@dataclass
class Point:
    x: float
    y: float
    z: float

    def __add__(self, other: Union["Point", int, float]) -> "Point":
        if type(other) == int or type(other) == float:
            point = Point(self.x + other, self.y + other, self.z + other)
        elif type(other) == Point:
            point = Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")
        return point

    def __sub__(self, other: Union["Point", int, float]) -> "Point":
        if type(other) == int or type(other) == float:
            point = Point(self.x - other, self.y - other, self.z - other)
        elif type(other) == Point:
            point = Point(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(self)}' and '{type(other)}'")
        return point

    def __mul__(self, other: Union[int, float]):
        if type(other) != int and type(other) != float:
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(other)}'")
        return Point(self.x * other, self.y * other, self.z * other)

    def __str__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def rotate_z(self, angle: Union[int, float]) -> "Point":
        """Rotate points around the z axis by angle in radians"""
        return Point(
            self.x * math.cos(angle) - self.x * math.sin(angle),
            self.x * math.sin(angle) + self.x * math.cos(angle),
            self.z,
        )

    def norm(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def list(self) -> List[Union[int, float]]:
        return [self.x, self.y, self.z]


def world_to_camera(point: "Point", camera: Dict[str, Any]) -> "Point":
    """Transforms a point to coordinates with the camera at the origin and the x-axis perpendicular to the image
    axis towards the focus."""

    # TODO: there appears to be a bug in this implementation
    pos = camera["pos"]
    f = camera["f"]
    theta = math.atan2(pos.y, -pos.x)
    point_in_cam_coords = (point - pos).rotate_z(theta)
    x = point_in_cam_coords.x
    y = point_in_cam_coords.y
    scale = x / f
    camera_point = Point(scale * point_in_cam_coords.z, scale * y, scale)
    return camera_point


def render_points(
        points: List["Point"],
        view: Dict[str, float],
        fit_params: Dict[str, "Point"] = None,
        dims: Tuple[int, int] = (320, 320),
) -> Image.Image:
    """Creates an image of the points and the fitted plane from the view of the camera at a position given in view.
    The view dictionary defines the position of the camera in the x,y plane by an angle in radians and a distance
    that, the camera points towards the origin."""

    img = Image.new("RGB", dims)
    img_draw = ImageDraw.Draw(img)
    rotation = view["rotation"]
    distance = view["distance"]
    camera_position = Point(distance * math.cos(rotation), distance * math.sin(rotation), 0)
    camera = {"pos": camera_position, "f": view["focal_length"] / 1000}  # pos - camera position, f - focal length in m
    if fit_params:
        # TODO: implement colouring of the image using the distance to the plane. Also add in transparency for points
        #  behind the plan and opacity for points in front of the plane
        pass
    for point in points:
        # TODO: sort points along camera axis to get display ordering correct when drawing
        point_in_image = world_to_camera(point, camera)
        size = 100 / point_in_image.z
        logger.debug(f"World {point}: size {size} at {point_in_image}")
        y = point_in_image.x + dims[0] // 2
        x = point_in_image.y + dims[1] // 2
        img_draw.ellipse((x - size, y - size, x + size, y + size), fill=(250, 0, 0), outline=(0, 255, 0))
    return img


def fit_points(points: List[Tuple[float, float, float]]) -> Dict[str, "Point"]:
    """Takes a  list of input points and calculates the plane of best fit."""
    # TODO: implementation to return plane defined by point and normal
    plane_coefficients = get_plane_coefficients(points)
    point_z = (-plane_coefficients[3]/-plane_coefficients[2])
    point = Point(0, 0, point_z)
    normal = Point(plane_coefficients[0], plane_coefficients[1], plane_coefficients[2])
    normal = normal * (1 / normal.norm())
    return {"point": point, "normal": normal}


def get_plane_coefficients(points: List[Tuple[float, float, float]]) -> Tuple[float, float, float, float]:
    points_np = np.array(points)
    val_type = np.float64

    n = points_np.shape[0]
    if n < 3:
        return 0, 0, 0, 0

    total = np.zeros(3, dtype=val_type)
    for p in points_np:
        total += p
    centroid = total * (1.0 / val_type(n))

    xx = 0.0
    xy = 0.0
    xz = 0.0
    yy = 0.0
    yz = 0.0
    zz = 0.0
    for p in points_np:
        r = p - centroid
        xx += r[0] * r[0]
        xy += r[0] * r[1]
        xz += r[0] * r[2]
        yy += r[1] * r[1]
        yz += r[1] * r[2]
        zz += r[2] * r[2]
    xx /= val_type(n)
    xy /= val_type(n)
    xz /= val_type(n)
    yy /= val_type(n)
    yz /= val_type(n)
    zz /= val_type(n)

    weighted_dir = np.zeros(3, dtype=val_type)
    axis_dir = np.zeros(3, dtype=val_type)

    # X COMPONENT
    det_x = (yy * zz) - (yz * yz)
    axis_dir[0] = det_x
    axis_dir[1] = (xz * yz) - (xy * zz)
    axis_dir[2] = (xy * yz) - (xz * yy)
    weight = det_x * det_x
    if np.dot(weighted_dir, axis_dir) < 0.0:
        weight *= -1.0
    weighted_dir += axis_dir * weight

    # Y COMPONENT
    det_y = (xx * zz) - (xz * xz)
    axis_dir[0] = (xz * yz) - (xy * zz)
    axis_dir[1] = det_y
    axis_dir[2] = (xy * xz) - (yz * xx)
    weight = det_y * det_y
    if np.dot(weighted_dir, axis_dir) < 0.0:
        weight *= -1.0
    weighted_dir += axis_dir * weight

    # Z COMPONENT
    det_z = (xx * yy) - (xy * xy)
    axis_dir[0] = (xy * yz) - (xz * yy)
    axis_dir[1] = (xy * xz) - (yz * xx)
    axis_dir[2] = det_z
    weight = det_z * det_z
    if np.dot(weighted_dir, axis_dir) < 0.0:
        weight *= -1.0
    weighted_dir += axis_dir * weight

    a = weighted_dir[0]
    b = weighted_dir[1]
    c = weighted_dir[2]
    d = np.dot(weighted_dir, centroid) * -1.0  # Multiplication by -1 preserves the sign (+) of D on the LHS
    normalization_factor = math.sqrt((a * a) + (b * b) + (c * c))
    if normalization_factor == 0:
        return 0, 0, 0, 0
    elif normalization_factor != 1.0:  # Skips normalization if already normalized
        a /= normalization_factor
        b /= normalization_factor
        c /= normalization_factor
        d /= normalization_factor
    # Returns a float 4-tuple of the A/B/C/D coefficients such that (Ax + By + Cz + D == 0)
    return a, b, c, d


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    req_data = {
        "points": [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (-1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, -1.0, 0.0),
            (0.0, 0.0, 1.0),
            (0.0, 0.0, -1.0),
        ],
        "params": {"rotation": 0, "distance": 2.0, "focal_length": 50.0},
    }

    # Test fit_points() function
    point_normal = fit_points(req_data["points"])
    print(f"Point: {point_normal['point']}, Normal: {point_normal['normal']}")

    points_in = [Point(*p) for p in req_data["points"]]
    img_out = render_points(points_in, req_data["params"])
    # TODO: should show up as:
    #
    #        o
    #
    #    o   0   o
    #
    #        o

    img_out.show()
