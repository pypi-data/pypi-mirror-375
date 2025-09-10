from __future__ import annotations

import multiprocessing
from functools import partial
from multiprocessing import Pool
from numbers import Number
from typing import Any
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

import numpy
import tqdm
from silx.utils.enum import Enum as _Enum

from ..io.utils import create_nxdata_dict
from ..processing.rocking_curves import FitMethod
from ..processing.rocking_curves import fit_2d_rocking_curve
from ..processing.rocking_curves import fit_rocking_curve
from .data import Data
from .utils import NoDimensionsError
from .utils import TooManyDimensionsForRockingCurvesError

Indices = Union[range, numpy.ndarray]
DataLike = Union[Data, numpy.ndarray]


class Maps_1D(_Enum):
    """Names of the fitting parameters of the 1D fit result. Each result is a map of frame size."""

    AMPLITUDE = "Amplitude"
    FWHM = "FWHM"
    PEAK = "Peak position"
    BACKGROUND = "Background"


class Maps_2D(_Enum):
    """Names of the fitting parameters of the 2D fit result. Each result is a map of frame size."""

    AMPLITUDE = "Amplitude"
    PEAK_X = "Peak position first motor"
    PEAK_Y = "Peak position second motor"
    FWHM_X = "FWHM first motor"
    FWHM_Y = "FWHM second motor"
    BACKGROUND = "Background"
    CORRELATION = "Correlation"


MAPS_1D: Tuple[Maps_1D] = Maps_1D.values()
MAPS_2D: Tuple[Maps_2D] = Maps_2D.values()


def generator(
    data: DataLike, moments: numpy.ndarray | None = None, indices=None
) -> (
    Generator[Tuple[float, None], None, None]
    | Generator[Tuple[float, float], None, None]
):
    """
    Generator that returns the rocking curve for every pixel

    :param ndarray data: data to analyse
    :param moments: array of same shape as data with the moments values per pixel and image, optional
    :type moments: Union[None, ndarray]
    """
    for i in range(data.shape[1]):
        for j in range(data.shape[2]):
            if indices is None:
                new_data = data[:, i, j]
            else:
                new_data = numpy.zeros(data.shape[0])
                new_data[indices] = data[indices, i, j]
            if moments is not None:
                yield new_data, moments[:, i, j]
            yield new_data, None


def fit_data(
    data: DataLike,
    moments: numpy.ndarray | None = None,
    values: List[numpy.ndarray] | numpy.ndarray | None = None,
    shape: Any = None,
    indices: Indices | None = None,
    int_thresh: Number = 15,
    method: FitMethod | None = None,
):
    """Fit data in axis 0 of data"""

    g = generator(data, moments)
    cpus = multiprocessing.cpu_count()
    curves, maps = [], []
    with Pool(cpus - 1) as p:
        for curve, pars in tqdm.tqdm(
            p.imap(
                partial(
                    fit_rocking_curve,
                    x_values=values,
                    int_thresh=int_thresh,
                    method=method,
                ),
                g,
            ),
            total=data.shape[1] * data.shape[2],
        ):
            curves.append(list(curve))
            maps.append(list(pars))

    return numpy.array(curves).T.reshape(data.shape), numpy.array(maps).T.reshape(
        (4, data.shape[-2], data.shape[-1])
    )


def fit_2d_data(
    data: DataLike,
    values: List[numpy.ndarray] | numpy.ndarray,
    shape: Tuple[int, int],
    moments: numpy.ndarray | None = None,
    int_thresh: int = 15,
    indices: Indices | None = None,
    method: FitMethod | None = None,
):
    """Fit data in axis 0 of data"""
    g = generator(data, moments, indices)
    cpus = multiprocessing.cpu_count()
    curves, maps = [], []
    with Pool(cpus - 1) as p:
        for curve, pars in tqdm.tqdm(
            p.imap(
                partial(
                    fit_2d_rocking_curve,
                    x_values=values,
                    shape=shape,
                    int_thresh=int_thresh,
                    method=method,
                ),
                g,
            ),
            total=data.shape[-2] * data.shape[-1],
        ):
            curves.append(list(curve))
            maps.append(list(pars))

    curves = numpy.array(curves).T
    if indices is not None:
        curves = curves[indices]
    return curves.reshape(data[indices].shape), numpy.array(maps).T.reshape(
        (7, data.shape[-2], data.shape[-1])
    )


def generate_rocking_curves_nxdict(
    dataset,  # ImageDataset. Cannot type due to circular import
    maps: numpy.ndarray,
    residuals: numpy.ndarray | None,
) -> dict:
    if not dataset.dims.ndim:
        raise NoDimensionsError("generate_rocking_curves_nxdict")
    entry = "entry"

    nx = {
        entry: {"@NX_class": "NXentry"},
        "@NX_class": "NXroot",
        "@default": entry,
    }

    if dataset.transformation:
        axes = [
            dataset.transformation.yregular,
            dataset.transformation.xregular,
        ]
        axes_names = ["y", "x"]
        axes_long_names = [
            dataset.transformation.label,
            dataset.transformation.label,
        ]
    else:
        axes = None
        axes_names = None
        axes_long_names = None

    if dataset.dims.ndim == 1:
        map_names = MAPS_1D
    elif dataset.dims.ndim == 2:
        map_names = MAPS_2D
    else:
        raise TooManyDimensionsForRockingCurvesError()

    for i, map_name in enumerate(map_names):
        signal = maps[i]
        nx[entry][map_name] = create_nxdata_dict(
            signal, map_name, axes, axes_names, axes_long_names
        )
    if residuals is not None:
        nx[entry]["Residuals"] = create_nxdata_dict(
            residuals, "Residuals", axes, axes_names, axes_long_names
        )
    nx[entry]["@default"] = Maps_1D.AMPLITUDE.value

    return nx


def compute_residuals(
    target_dataset,  # ImageDataset. Cannot type due to circular import
    original_dataset,  # ImageDataset. Cannot type due to circular import
    indices: numpy.ndarray | None,
):
    return numpy.sqrt(
        numpy.subtract(target_dataset.zsum(indices), original_dataset.zsum(indices))
        ** 2
    )
