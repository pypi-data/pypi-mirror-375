from __future__ import annotations

from typing import Literal
from typing import Tuple

import numpy
import tqdm
from silx.math.medianfilter import medfilt2d
from skimage.transform import rescale

import darfix

from ..io.progress import display_progress
from ..math import Vector3D


def compute_moments(values, data, smooth: bool = True):
    """
    Compute first, second, third and fourth moment of data on values.

    :param values: 1D array of X-values
    :param data: nD array of Y-values with `len(weight) == len(values)`
    :returns: The four first moments to distribution Y(X)
    """
    if len(values) != len(data):
        raise ValueError("the length of 'values' and 'data' is not equal")

    wsum = numpy.sum(data, axis=0, dtype=numpy.float64)
    values = numpy.asarray(values, dtype=numpy.float64)

    # Moments
    # mean = sum(w * x) / sum(w)
    # var  = sum(w * (x - mean)^2) / sum(w)
    # skew = sum(w * ((x - mean)/sigma)^3) / sum(w)
    # kurt = sum(w * ((x - mean)/sigma)^4) / sum(w) - 3
    #
    # The loops below are there to avoid creating another array
    # in memory with the same shape as `weights`.

    with numpy.errstate(invalid="ignore", divide="ignore"):
        mean = sum(
            w * x
            for x, w in zip(
                display_progress(values, desc="Moments: compute mean 1/4"), data
            )
        )
        mean /= wsum

        var = sum(
            w * ((x - mean) ** 2)
            for x, w in zip(
                display_progress(values, desc="Moments: compute var 2/4"), data
            )
        )
        var /= wsum
        sigma = numpy.sqrt(var)
        fwhm = darfix.config.FWHM_VAL * sigma

        skew = sum(
            w * (((x - mean) / sigma) ** 3)
            for x, w in zip(
                display_progress(values, desc="Moments: compute skew 3/4"), data
            )
        )
        skew /= wsum

        kurt = sum(
            w * (((x - mean) / sigma) ** 4)
            for x, w in zip(
                display_progress(values, desc="Moments: compute kurt 4/4"), data
            )
        )
        kurt /= wsum
        kurt -= 3  # Fisher’s definition

    if smooth:
        mean = medfilt2d(mean)
        fwhm = medfilt2d(fwhm)
        skew = medfilt2d(skew)
        kurt = medfilt2d(kurt)

    return mean, fwhm, skew, kurt


def compute_peak_position(data, values=None, center_data=False):
    """
    Compute peak position map

    :param bool center_data: If True, the values are centered on 0.
    """
    if values is not None:
        values = numpy.asanyarray(values)
        x = numpy.array(numpy.argmax(data, axis=0))
        if center_data:
            middle = float(min(values) + numpy.ptp(values)) / 2
            values -= middle
        image = [values[i] for i in x.flatten()]
        image = numpy.reshape(image, x.shape)
    else:
        image = numpy.array(numpy.argmax(data, axis=0))
        if center_data:
            middle = len(data) / 2
            vals = numpy.linspace(-middle, middle, len(data))
            image = image * numpy.ptp(vals) / len(data) + numpy.min(vals)
    return image


def compute_rsm(
    H: int, W: int, d: float, ffz: float, mainx: float, rotate: bool = False
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    Transformation to azimuthal coordinates.

    :param int H: height of the image in pixels.
    :param int W: width of the image in pixels.
    :param float d: Distance in micrometers of each pixel.
    :param float ffz: motor 'ffz' value.
    :param float mainx: motor 'mainx' value.

    :returns: Tuple of two arrays of size (W, H)
    :rtype: (X1, X2) : ndarray
    """
    if rotate:
        y = (numpy.arange(H) - H / 2) * d
        z = ffz - (W / 2 - numpy.arange(W)) * d
        y, z = numpy.meshgrid(y, z, indexing="ij")
    else:
        y = (numpy.arange(W) - W / 2) * d
        z = ffz - (H / 2 - numpy.arange(H)) * d
        z, y = numpy.meshgrid(z, y, indexing="ij")
    eta = numpy.arctan2(y, z)
    twotheta = numpy.arctan2(numpy.sqrt(y * y + z * z), mainx)
    return numpy.degrees(eta), numpy.degrees(twotheta)


def compute_magnification(
    H: int,
    W: int,
    d: float,
    obx: float,
    obpitch: float,
    mainx: float,
    topography_orientation: int | None = None,
    center: bool = True,
) -> Tuple[numpy.ndarray, numpy.ndarray]:
    """
    :param int H: height of the image in pixels.
    :param int W: width of the image in pixels.
    :param float d: Distance in micrometers of each pixel.
    :param float obx: motor 'obx' value.
    :param float obpitch: motor 'obpitch' value in the middle of the dataset.
    :param float mainx: motor 'mainx' value.

    :returns: Tuple of two arrays of size (H, W)
    :rtype: (X1, X2) : ndarray
    """

    pix_arr = list(numpy.meshgrid(numpy.arange(H), numpy.arange(W)))
    d1 = obx / numpy.cos(numpy.radians(obpitch))
    d2 = mainx / numpy.cos(numpy.radians(obpitch)) - d1
    M = d2 / d1
    d /= M
    if center:
        pix_arr[0] = (pix_arr[0] - W / 2) * d
        pix_arr[1] = (H / 2 - pix_arr[1]) * d
    else:
        pix_arr[0] = pix_arr[0] * d
        pix_arr[1] = (H - 1 - pix_arr[1]) * d
    if topography_orientation is not None:
        pix_arr[topography_orientation] /= numpy.sin(numpy.radians(obpitch))
    return pix_arr[0], pix_arr[1]


def rescale_data(data, scale):
    new_data = None
    for i, image in enumerate(data):
        simage = rescale(image, scale, anti_aliasing=True, preserve_range=True)
        if new_data is None:
            new_data = numpy.empty((len(data),) + simage.shape, dtype=data.dtype)
        new_data[i] = simage
    return new_data


def calculate_RSM_histogram(
    data: numpy.ndarray,
    diffry_values: numpy.ndarray,
    twotheta: numpy.ndarray,
    eta: numpy.ndarray,
    Q: Vector3D,
    a: float,
    map_range: float,
    units: Literal["poulsen", "gorfman"] | None = None,
    map_shape: Vector3D | None = None,
    n: Vector3D | None = None,
    E: float | None = None,
):
    """
    ***Code originally written by Mads Carslen***

    Calculate reciprocal space map from a 'diffry' scan without the objective lens.
    The RSM is calculated as a multidimensional histogram;

    :param data:
    :param diffry_values:
    :param twotheta:
    :param eta:
    :param Q: Scattering vector in oriented pseudocubic coordinates.
    :param a: pseudocubic lattice parameter
    :param map_range: range (in all 3 directions) of the histogram. Center-to edge-distance.
    :param units: either 'poulsen'  [10.1107/S1600576717011037] or 'gorfman' [https://arxiv.org/pdf/2110.14311.pdf]. Default: 'poulsen'
    :param map_shape: Number of bins in each direction
    :param n: surface normal of the sample in oriented pseudocubic hkl
    :param E: energy
    """

    if units is None:
        units = "poulsen"
    if map_shape is None:
        map_shape = (50, 50, 50)
    if n is None:
        n = (1, 0, 0)
    if E is None:
        E = 17.0

    k = 2 * numpy.pi / (12.391 / E)

    diffry_center = numpy.mean(diffry_values)
    img_shape = data[0].shape
    if units == "gorfman":
        # Build orientation matrix
        sampl_z = numpy.array(Q) / numpy.linalg.norm(
            numpy.array(Q)
        )  # assume scattering vector is z
        sampl_x = n - sampl_z * numpy.dot(sampl_z, n) / numpy.linalg.norm(
            n
        )  # orthogonalize
        sampl_x /= numpy.linalg.norm(sampl_x)  # nomalize

        sampl_y = numpy.cross(sampl_z, sampl_x)
        lab_to_lat = numpy.stack((sampl_x, sampl_y, sampl_z))
    elif units == "poulsen":
        lab_to_lat = numpy.identity(3)

    # Calculate lab frame q vector for each pixel
    k0 = numpy.array([k, 0, 0])  # Lab frame incidetn wavevector
    twotheta = numpy.radians(twotheta)
    eta = numpy.radians(eta)
    kh = k * numpy.stack(
        [
            numpy.cos(twotheta),
            numpy.sin(twotheta) * numpy.sin(eta),
            numpy.sin(twotheta) * numpy.cos(eta),
        ]
    )  # Lab frame scattered wavevector
    q = kh - k0[:, numpy.newaxis, numpy.newaxis]
    if units == "gorfman":
        q = q * a / 2 / numpy.pi
    elif units == "poulsen":
        q = q * a / 2 / numpy.pi / numpy.linalg.norm(Q)

    # flatten to match syntax for histogramdd
    q = q.reshape(3, img_shape[0] * img_shape[1])
    # Rotate from lab frame to sample frame
    theta_ref = numpy.arcsin(2 * numpy.pi * numpy.linalg.norm(Q) / a / k / 2)
    q = numpy.stack(
        [
            q[0, ...] * numpy.cos(theta_ref) + q[2, ...] * numpy.sin(theta_ref),
            q[1, ...],
            q[2, ...] * numpy.cos(theta_ref) - q[0, ...] * numpy.sin(theta_ref),
        ]
    )

    # Make histogram ranges
    q_mean = numpy.mean(q, axis=1)
    diffry_mean = numpy.radians(numpy.mean(diffry_values) - diffry_center)
    q_mean = numpy.stack(
        [
            q_mean[0] * numpy.cos(diffry_mean) - q_mean[2] * numpy.sin(diffry_mean),
            q_mean[1],
            q_mean[2] * numpy.cos(diffry_mean) + q_mean[0] * numpy.sin(diffry_mean),
        ]
    )

    if units == "gorfman":
        q_mean = lab_to_lat.transpose() @ q_mean

    ranges = (
        (q_mean[0] - map_range, q_mean[0] + map_range),
        (q_mean[1] - map_range, q_mean[1] + map_range),
        (q_mean[2] - map_range, q_mean[2] + map_range),
    )  # hkl units

    # initialize sum arrays
    sum_inte = numpy.zeros(map_shape)
    sum_freq = numpy.zeros(map_shape)

    loop = tqdm.tqdm(data)
    # Loop through images
    for i, image in enumerate(loop):
        # read angle
        diffry = numpy.radians(diffry_values[i] - diffry_center)
        # rotate q back to zero-motor frame
        q_rot = numpy.stack(
            [
                q[0, ...] * numpy.cos(diffry) - q[2, ...] * numpy.sin(diffry),
                q[1, ...],
                q[2, ...] * numpy.cos(diffry) + q[0, ...] * numpy.sin(diffry),
            ]
        )
        # Rotate into lattice frame
        q_rot = lab_to_lat.transpose() @ q_rot
        # Do binning
        sum_inte += numpy.histogramdd(
            q_rot.transpose(), map_shape, ranges, weights=image.flatten()
        )[0]
        sum_freq += numpy.histogramdd(q_rot.transpose(), map_shape, ranges)[0]

    edges = numpy.histogramdd(q_rot.transpose(), map_shape, ranges)[1]
    # Setting sum_freq to NaN where it is 0 to avoid division by 0 (`arr` will be NaN there)
    sum_freq[sum_freq == 0] = numpy.nan
    arr = sum_inte / sum_freq

    if units == "poulsen":
        edges[2] = edges[2] - 1

    return arr, edges
