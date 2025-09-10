from __future__ import annotations

from typing import Any
from typing import Literal
from typing import Sequence

import numpy
from attr import dataclass
from matplotlib.colors import hsv_to_rgb
from silx.utils.enum import Enum

from darfix.io.utils import create_nxdata_dict

from ..math import SCALE_FACTOR
from .dataset import ImageDataset
from .utils import compute_hsv


class MomentType(Enum):
    COM = "Center of mass"
    FWHM = "FWHM"
    SKEWNESS = "Skewness"
    KURTOSIS = "Kurtosis"


@dataclass
class OrientationDistData:
    data: numpy.ndarray
    as_rgb: numpy.ndarray


@dataclass
class ImageParameters:
    xlabel: str
    ylabel: str
    scale: tuple[int, int]
    origin: tuple[float, float]


@dataclass
class OrientationDistImage(ImageParameters):
    data: numpy.ndarray
    as_rgb: numpy.ndarray
    contours: dict


class MultiDimMomentType(Enum):
    """Moments that are only computed for datasets with multiple dimensions"""

    ORIENTATION_DIST = "Orientation distribution"
    MOSAICITY = "Mosaicity"


def get_axes(transformation: numpy.ndarray | None) -> tuple[
    tuple[numpy.ndarray, numpy.ndarray] | None,
    tuple[str, str] | None,
    tuple[str, str] | None,
]:
    if not transformation:
        return None, None, None

    axes = (transformation.yregular, transformation.xregular)
    axes_names = ("y", "x")
    axes_long_names = (transformation.label, transformation.label)

    return axes, axes_names, axes_long_names


def compute_normalized_component(component: numpy.ndarray):
    no_nans_indices = ~numpy.isnan(component)
    min_component = numpy.min(
        component[no_nans_indices] if len(component[no_nans_indices]) > 0 else component
    )
    component[numpy.isnan(component)] = min_component
    return 2 * (component - min_component) / numpy.ptp(component) - 1


def compute_mosaicity(
    moments: dict[int, numpy.ndarray], x_dimension: int, y_dimension: int
):
    norm_center_of_mass_x = compute_normalized_component(moments[x_dimension][0])
    norm_center_of_mass_y = compute_normalized_component(moments[y_dimension][0])

    return hsv_to_rgb(compute_hsv(norm_center_of_mass_x, norm_center_of_mass_y))


def create_moment_nxdata_groups(
    parent: dict[str, Any],
    moment_data: numpy.ndarray,
    axes,
    axes_names,
    axes_long_names,
):

    for i, map_type in enumerate(MomentType.values()):
        parent[map_type] = create_nxdata_dict(
            moment_data[i],
            map_type,
            axes,
            axes_names,
            axes_long_names,
        )


def generate_grain_maps_nxdict(
    dataset: ImageDataset,
    mosaicity: numpy.ndarray | None,
    orientation_dist_image: OrientationDistImage | None,
) -> dict:
    moments = dataset.moments_dims
    axes, axes_names, axes_long_names = get_axes(dataset.transformation)

    nx = {
        "entry": {"@NX_class": "NXentry"},
        "@NX_class": "NXroot",
        "@default": "entry",
    }

    if mosaicity is not None:
        nx["entry"][MultiDimMomentType.MOSAICITY.value] = create_nxdata_dict(
            mosaicity,
            MultiDimMomentType.MOSAICITY.value,
            axes,
            axes_names,
            axes_long_names,
            rgba=True,
        )
        nx["entry"]["@default"] = MultiDimMomentType.MOSAICITY.value
    else:
        nx["entry"]["@default"] = MomentType.COM.value

    if orientation_dist_image is not None:
        nx["entry"][MultiDimMomentType.ORIENTATION_DIST.value] = {
            "key": {
                "image": orientation_dist_image.as_rgb,
                "data": orientation_dist_image.data,
                "origin": orientation_dist_image.origin,
                "scale": orientation_dist_image.scale,
                "xlabel": orientation_dist_image.xlabel,
                "ylabel": orientation_dist_image.ylabel,
                "image@interpretation": "rgba-image",
                "image@CLASS": "IMAGE",
            },
            "curves": orientation_dist_image.contours,
        }

    if dataset.dims.ndim <= 1:
        create_moment_nxdata_groups(
            nx["entry"],
            moments[0],
            axes,
            axes_names,
            axes_long_names,
        )
    else:
        for axis, dim in dataset.dims.items():
            nx["entry"][dim.name] = {"@NX_class": "NXcollection"}
            create_moment_nxdata_groups(
                nx["entry"][dim.name],
                moments[axis],
                axes,
                axes_names,
                axes_long_names,
            )

    return nx


def compute_orientation_dist_data(
    dataset: ImageDataset,
    x_dimension: int,
    y_dimension: int,
    third_motor: int | None = None,
) -> OrientationDistData | None:
    orientation_dist = dataset.compute_orientation_dist(
        x_dimension=x_dimension,
        y_dimension=y_dimension,
        third_motor=third_motor,
    )
    hsv_key = dataset.compute_orientation_colorkey(x_dimension, y_dimension)
    if orientation_dist is None:
        return None

    return OrientationDistData(data=orientation_dist, as_rgb=hsv_to_rgb(hsv_key))


def get_image_parameters(
    dataset: ImageDataset,
    x_dimension: int,
    y_dimension: int,
    origin: Literal["dims"] | Literal["center"] | None = None,
):
    xdim = dataset.dims[x_dimension]
    ydim = dataset.dims[y_dimension]

    x_com = dataset.moments_dims[x_dimension][0]
    y_com = dataset.moments_dims[y_dimension][0]

    x_min, x_max = numpy.min(x_com), numpy.max(x_com)
    y_min, y_max = numpy.min(y_com), numpy.max(y_com)

    xscale = (x_max - x_min) / xdim.size
    yscale = (y_max - y_min) / ydim.size

    if origin == "dims":
        image_origin = (x_min, y_min)
    elif origin == "center":
        image_origin = (
            -xscale * int(xdim.size / 2),
            -yscale * int(ydim.size / 2),
        )
    else:
        image_origin = (0, 0)

    return ImageParameters(
        xlabel=xdim.name,
        ylabel=ydim.name,
        origin=image_origin,
        scale=(xscale / SCALE_FACTOR, yscale / SCALE_FACTOR),
    )


def get_third_motor_index(other_dims_indices: Sequence[int]) -> int:
    if 0 not in other_dims_indices:
        return 0

    if 1 not in other_dims_indices:
        return 1

    return 2
