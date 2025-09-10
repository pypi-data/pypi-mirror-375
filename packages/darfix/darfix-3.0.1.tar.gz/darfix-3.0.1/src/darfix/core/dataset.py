from __future__ import annotations

import copy
import glob
import logging
import multiprocessing
import os
import warnings
from functools import partial
from multiprocessing import Pool
from typing import Dict
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import fabio
import h5py
import numpy
import silx
from silx.io import fabioh5
from silx.io.fabioh5 import EdfFabioReader
from silx.io.url import DataUrl
from silx.io.utils import h5py_read_dataset
from sklearn.exceptions import ConvergenceWarning

from darfix.core.data import Data
from darfix.core.data import Operation
from darfix.core.data import StateOfOperations
from darfix.core.dimension import AcquisitionDims
from darfix.core.dimension import find_dimensions_from_metadata
from darfix.core.imageOperations import Method
from darfix.core.imageOperations import background_subtraction
from darfix.core.imageOperations import background_subtraction_2D
from darfix.core.imageOperations import chunk_image
from darfix.core.imageOperations import hot_pixel_removal_2D
from darfix.core.imageOperations import hot_pixel_removal_3D
from darfix.core.imageOperations import img2img_mean
from darfix.core.imageOperations import mask_removal
from darfix.core.imageOperations import threshold_removal
from darfix.core.imageRegistration import apply_opencv_shift
from darfix.core.imageRegistration import shift_detection
from darfix.core.mapping import calculate_RSM_histogram
from darfix.core.mapping import compute_magnification
from darfix.core.mapping import compute_moments
from darfix.core.mapping import compute_rsm
from darfix.core.rocking_curves import MAPS_1D
from darfix.core.rocking_curves import MAPS_2D
from darfix.core.rocking_curves import fit_2d_data
from darfix.core.rocking_curves import fit_data
from darfix.core.roi import apply_2D_ROI
from darfix.core.roi import apply_3D_ROI
from darfix.core.utils import NoDimensionsError
from darfix.core.utils import TooManyDimensionsForRockingCurvesError
from darfix.core.utils import compute_hsv
from darfix.decomposition.ipca import IPCA
from darfix.decomposition.nica import NICA
from darfix.decomposition.nmf import NMF
from darfix.io import utils as io_utils

from ..math import SCALE_FACTOR
from ..math import Vector3D
from .transformation import Transformation

_logger = logging.getLogger(__file__)


class ImageDataset:
    """Class to define a dataset from a series of data files.
    The idea of this class is to make life easier for the user when using darfix.
    Most of the operations on darfix need to use all the data to be computed,
    having a wrapper like Dataset allows to execute the operations on that same data
    without having to load the data at each step.
    This is not a God object: Operations on the source data (e.g. blind source separation, hot pixel removal,
    shift correction) are implemented as pure transformations acting on this entity,
    such that there are no side effects and the operations can be chained together to define
    a computational workflow.
    Although it is a complex class due to the next things:
    - The data can be loaded on memory or on disk. When the data is on disk,
    the core operations are called using chunks of the data to reduce its size on memory.
    - A Dataset allows the user to use only part of the data for certain operations,
    which allows to have a much faster processing of those. This is done using the
    `indices` and `bg_indices` attributes.
    - It also allows, for certain operations and at certain cases, to stop a running operation.
    This is done with the attributes `running_data` and `state_of_operations`, which
    contain the `Data` object with the data being modified and a list of the operations
    to stop.
    - The `dims` attribute is a dictionary containing the dimensions that
    shape the data. Several operations can be applied on only part of the data
    depending on the dimensions shape.

    :param _dir: Global directory to use and save all the data in the different
        operations.
    :type _dir: str
    :param data: If not None, sets the Data array with the data of the dataset
        to use, default None
    :type data: :class:`Data`, optional
    :param raw_folder: Path to the folder that contains the data, defaults to
        None
    :type raw_folder: Union[None,str], optional
    :param filenames: Ordered list of filenames, defaults to None (expected for EDF files).
    :type filenames: Union[Generator,Iterator,List], optional
    :param dims: Dimensions dictionary
    :type dims: AcquisitionDims, optional
    :param transformation: Axes to use when displaying the images
    :type transformation: ndarray, optional
    :param in_memory: If True, data is loaded into memory, else, data is read in
        chunks depending on the algorithm to apply, defaults to False.
    :type in_memory: bool, optional
    :param copy_files: If True, creates a new treated data folder and doesn't replace
        the directory files.
    :type copy_files: bool, optional
    :param isH5: True if the data is contained into HDF5 file
    :param metadata_url: Optional url to the metadata (in case of non-EDF acquisition)
    """

    _DATASETS_USED_FOR_TRANSFORMATION = ("mainx", "ffz", "obx", "obpitch")
    """A couple of dataset with hard-coded named used for transformation"""

    def __init__(
        self,
        _dir: str,
        data: Data | None = None,
        raw_folder: str | None = None,
        first_filename: str | None = None,
        filenames: Sequence[str] | None = None,
        dims: AcquisitionDims | None = None,
        transformation: numpy.ndarray | None = None,
        in_memory: bool = True,
        copy_files: bool = False,
        isH5: bool = False,
        title: str | None = None,
        metadata_url: DataUrl | str | None = None,
    ):
        self._data = None
        self._frames_intensity = []
        self.running_data = None
        self.moments_dims = {}
        self.state_of_operations = StateOfOperations()
        self._dir = _dir
        self._transformation = transformation
        self._title = title or ""
        if copy_files:
            self._dir = os.path.join(self._dir, "treated")
            try:
                os.makedirs(self._dir, exist_ok=True)
            except PermissionError:
                raise PermissionError(
                    "Add a directory in the Treated Data tab with WRITE permission"
                )

        if dims is None:
            self.__dims = AcquisitionDims()
        else:
            assert isinstance(
                dims, AcquisitionDims
            ), "Attribute dims has to be of class AcquisitionDims"
            self.__dims = dims
        # Keys: dimensions names, values: dimensions values
        self._dimensions_values = {}

        self._in_memory = in_memory
        self._isH5 = isH5

        if data is not None:
            self._data = data
        else:
            if filenames is None and first_filename is None:
                search_dir = _dir if raw_folder is None else raw_folder
                paths = glob.glob(os.path.join(search_dir, "*"))
                filenames = sorted([path for path in paths if os.path.isfile(path)])
            self.filenames = filenames
            self.first_filename = first_filename

            if self._isH5:
                data_urls, metadata_readers = self._init_hdf5_data_urls(
                    first_filename, metadata_url
                )
            else:
                data_urls, metadata_readers = self._init_image_data_urls(
                    first_filename, filenames
                )

            self._data = Data(
                numpy.array(data_urls),
                metadata=metadata_readers,
                in_memory=self._in_memory,
            )

    @staticmethod
    def _init_image_data_urls(first_filename, filenames):
        """Data URL and metadata reader for each image in a list of files (most likely EDF)"""
        metadata_readers = []
        data_urls = []

        with fabio.open_series(
            filenames=filenames, first_filename=first_filename
        ) as series:
            for frame in series.frames():
                filename = frame.file_container.filename
                data_urls.append(DataUrl(file_path=filename, scheme="fabio"))
                fabio_reader = fabioh5.EdfFabioReader(file_name=filename)
                metadata_readers.append(fabio_reader)
                fabio_reader.close()

        return data_urls, metadata_readers

    def _init_hdf5_data_urls(
        self, data_url: Union[str, DataUrl], metadata_url: Union[str, DataUrl]
    ):
        """Data URL and metadata reader for each image in a 3D HDF5 dataset"""
        # Data URL for each image
        if not isinstance(data_url, DataUrl):
            data_url = DataUrl(data_url)

        with silx.io.open(data_url.file_path()) as h5:
            if not data_url.data_path() in h5:
                raise KeyError(
                    f"data path {data_url.data_path()} does not exist in {data_url.file_path()}"
                )
            hdf5_item = h5[data_url.data_path()]
            if not isinstance(hdf5_item, h5py.Dataset):
                raise ValueError(
                    f"url data path is not pointing to a HDF5 dataset but to {type(hdf5_item)}"
                )
            n_frames = hdf5_item.shape[0]

        data_urls = [
            DataUrl(
                file_path=data_url.file_path(),
                data_path=data_url.data_path(),
                data_slice=i,
                scheme="silx",
            )
            for i in range(n_frames)
        ]

        # Metadata dict associated to each image
        if metadata_url is None:
            frame_metadata = [{} for _ in range(n_frames)]
        else:
            if not isinstance(metadata_url, DataUrl):
                metadata_url = DataUrl(metadata_url)
            with silx.io.open(metadata_url.file_path()) as h5:
                metadata_path = metadata_url.data_path()
                if metadata_path not in h5:
                    raise KeyError(
                        f"Unable to find metadata path {metadata_path} in {metadata_url.file_path()}"
                    )

                datasets = extract_positioners(h5[metadata_path])
                frame_metadata = [
                    self._extract_hdf5_metadata(datasets, frame_index)
                    for frame_index in range(n_frames)
                ]

        metadata_readers = [
            _HDF5MetadataReader(metadata=mdata) for mdata in frame_metadata
        ]

        return data_urls, metadata_readers

    @staticmethod
    def _extract_hdf5_metadata(
        datasets: Dict[str, h5py.Dataset], frame_index: int
    ) -> dict:
        metadata = {}
        for name, dset in datasets.items():
            if name in ImageDataset._DATASETS_USED_FOR_TRANSFORMATION:
                if numpy.isscalar(dset):
                    metadata[name] = dset
                else:
                    metadata[name] = dset[frame_index]
            elif not numpy.isscalar(dset) and len(dset) <= frame_index:
                # case there is some missing metadata. (a 1D numpy array contains less points that there is frame)
                _logger.warning(
                    f"Unable to access index {frame_index} of the dataset {name}"
                )
                # handling is done later in `extract_metadata_values` by filling the missing values with `NaN`
                pass
            else:
                metadata[name] = dset[frame_index]
        return metadata

    def stop_operation(self, operation):
        """
        Method used for cases where threads are created to apply functions to the dataset.
        If method is called, the flag concerning the stop is set to 0 so that if the concerned
        operation is running in another thread it knows to stop.

        :param int operation: operation to stop
        :type int: Union[int, `Operation`]
        """
        if self.state_of_operations.is_running(operation):
            self.state_of_operations.stop(operation)
        if self.running_data is not None:
            self.running_data.stop_operation(operation)

    @property
    def transformation(self):
        return self._transformation

    @transformation.setter
    def transformation(self, value):
        self._transformation = value

    @property
    def title(self):
        return self._title

    @property
    def dir(self):
        return self._dir

    @property
    def is_h5(self):
        return self._isH5

    def compute_frames_intensity(self, kernel=(3, 3), sigma=20):
        """
        Returns for every image a number representing its intensity. This number
        is obtained by first blurring the image and then computing its variance.
        """
        _logger.info("Computing intensity per frame")
        io_utils.advancement_display(0, self.nframes, "Computing intensity")
        frames_intensity = []
        with self.state_of_operations.run_context(Operation.PARTITION):
            for i in range(self.nframes):
                import cv2

                if not self.state_of_operations.is_running(Operation.PARTITION):
                    return
                frames_intensity += [
                    cv2.GaussianBlur(self.get_data(i), kernel, sigma).var()
                ]
                io_utils.advancement_display(i + 1, self.nframes, "Computing intensity")
            self._frames_intensity = frames_intensity
            return frames_intensity

    def partition_by_intensity(
        self,
        bins: Optional[int] = None,
        bottom_bin: Optional[int] = None,
        top_bin: Optional[int] = None,
    ):
        """
        :param bins: number of bins to used for computing the frame intensity histogram
        :param bottom_bin: index of the bins to retrieve bottom threshold filter value. If not provided, there will be no bottom threshold (default).
        :param top_bin: index of the bins to retrieve top threshold filter value. If not provided, there will be no top threshold (default).

        Function that computes the data from the set of urls.
        If the filter_data flag is activated it filters the data following the next:
        -- First, it computes the intensity for each frame, by calculating the variance after
        passing a gaussian filter.
        -- Second, computes the histogram of the intensity.
        -- Finally, saves the data of the frames with an intensity bigger than a threshold.
        The threshold is set to be the second bin of the histogram.
        """
        frames_intensity = (
            self._frames_intensity
            if self._frames_intensity
            else self.compute_frames_intensity()
        )
        if frames_intensity is None:
            return
        _, bins = numpy.histogram(
            frames_intensity, self.nframes if bins is None else bins
        )
        frames_intensity = numpy.asanyarray(frames_intensity)
        if top_bin is None:
            top_bin = len(bins) - 1
        if bottom_bin is None:
            bottom_bin = 0

        bottom_threshold = frames_intensity >= bins[bottom_bin]
        top_threshold = frames_intensity <= bins[top_bin]
        threshold = numpy.array(
            [a and b for a, b in zip(bottom_threshold, top_threshold)]
        )
        return numpy.flatnonzero(threshold), numpy.flatnonzero(~threshold)

    @property
    def in_memory(self):
        return self._in_memory

    @in_memory.setter
    def in_memory(self, in_memory):
        """
        Removes data from memory and sets that from now on data will be read from disk.
        """
        if self._in_memory is not in_memory:
            self._in_memory = in_memory
            self._data = Data(self.data.urls, self.data.metadata, self._in_memory)

    @property
    def data(self):
        return self._data

    def get_data(self, indices=None, dimension=None, return_indices=False):
        """
        Returns the data corresponding to certains indices and given some dimensions values.
        The data is always flattened to be a stack of images.

        :param array_like indices: If not None, data is filtered using this array.
        :param array_like dimension: If not None, return only the data corresponding to
            the given dimension. Dimension is a 2d vector, where the first component is
            a list of the axis and the second is a list of the indices of the values to extract.
            The dimension and value list length can be up to the number of dimensions - 1.
            The call get_data(dimension=[[1, 2], [2, 3]]) is equivalent to data[:, 2, 3] when data
            is in memory.
            The axis of the dimension is so that lower the axis, fastest the dimension (higher changing
            value).

        :return: Array with the new data.
        """
        if dimension is not None and len(self._data.shape) > 3:
            # Make sure dimension and value are lists
            if isinstance(dimension[0], int):
                dimension[0] = [dimension[0]]
                dimension[1] = [dimension[1]]
            data = self.data

            # Init list of bool indices
            bool_indices = numpy.zeros(self.data.nframes, dtype=bool)
            if indices is None:
                indices = numpy.arange(self.nframes)
            bool_indices[indices] = True
            bool_indices = bool_indices.reshape(self.data.scan_shape)
            indx = numpy.arange(self.nframes).reshape(self.data.scan_shape)

            # For every axis, get corresponding elements
            for i, dim in enumerate(sorted(dimension[0])):
                # Flip axis to be consistent with the data shape
                axis = self.dims.ndim - dim - 1
                data = data.take(indices=dimension[1][i], axis=axis)
                bool_indices = bool_indices.take(indices=dimension[1][i], axis=axis)
                indx = indx.take(indices=dimension[1][i], axis=axis)

            data = data[bool_indices]
            indx = indx[bool_indices]
            if return_indices:
                return data.flatten(), indx.flatten()
            return data.flatten()

        data = self.data.flatten()
        if return_indices:
            if indices is None:
                indices = numpy.arange(self.nframes)
            return data[indices], indices
        if indices is None:
            return data
        return data[indices]

    @property
    def nframes(self):
        """
        Return number of frames
        """
        if self.data is None:
            return 0
        return self.data.nframes

    def to_memory(self, indices):
        """
        Method to load only part of the data into memory.
        Returns a new dataset with the data corresponding to given indices into memory.
        The new indices array has to be given, if all the data has to be set into
        memory please set `in_memory` to True instead, this way no new dataset will be
        created.

        :param array_like indices: Indices of the new dataset.
        """
        if not self._in_memory:
            data = self.get_data(indices)
            new_data = Data(data.urls, data.metadata, True)
        else:
            new_data = self.get_data(indices)
        return ImageDataset(
            _dir=self._dir,
            data=new_data,
            dims=self.__dims,
            in_memory=True,
            title=self.title,
        )

    @property
    def dims(self):
        return self.__dims

    @dims.setter
    def dims(self, _dims):
        if not isinstance(_dims, AcquisitionDims):
            raise TypeError(
                "Dimensions dictionary has " "to be of class `AcquisitionDims`"
            )
        self.__dims = _dims

    def zsum(self, indices=None, dimension=None):
        data = self.get_data(indices, dimension)
        return data.sum(axis=0)

    def reshape_data(self):
        """
        Function that reshapes the data to fit the dimensions.
        """
        ndim = self.__dims.ndim
        if ndim == 0:
            raise ValueError("No dimensions are listed")

        if ndim == 1:
            nframes_expected = self.__dims.get(0).size
            if nframes_expected != self.nframes:
                dimension = " ".join(self.__dims.get_names())
                raise ValueError(
                    f"Dimension {dimension} has {nframes_expected} points while there are {self.nframes} images. Try using other tolerance or step values."
                )
            return self

        dims_shape = self.__dims.shape
        org_data = self.get_data()
        org_shape = org_data.shape
        img_shape = (org_shape[-2], org_shape[-1])
        new_shape = dims_shape + img_shape
        try:
            data = org_data.reshape(new_shape)
        except Exception:
            dimensions = " ".join(self.__dims.get_names())
            raise ValueError(
                f"Dimensions {dimensions} have {dims_shape} points while there are {org_shape[:-2]} images. Try using other tolerance or step values."
            )

        return ImageDataset(
            _dir=self.dir,
            data=data,
            dims=self.__dims,
            in_memory=self._in_memory,
            title=self.title,
        )

    def find_dimensions(self, tolerance: float = 1e-9) -> None:
        """
        Call core.dimension.find_dimensions_from_metadata to set __dims

        :param tolerance: Tolerance used to find dimensions
        """
        self.__dims = find_dimensions_from_metadata(self.get_metadata_dict(), tolerance)

    def get_metadata_dict(self) -> dict[str, numpy.ndarray]:
        return {key: self.get_metadata_values(key) for key in self.get_metadata_keys()}

    def get_metadata_keys(self) -> numpy.ndarray:
        """
        Get all metadata keys (like positioner names)
        """
        return extract_metadata_keys(self.get_data().metadata)

    def get_metadata_values(self, key, indices=None, dimension=None) -> numpy.ndarray:
        metadata = self.get_data(indices, dimension).metadata
        values = extract_metadata_values(
            metadata,
            key,
            missing_value=numpy.nan,
            take_previous_when_missing=True,
        )
        if numpy.isscalar(values):
            return values
        else:
            return numpy.asarray(values)  # makes sure they all have the same dtype

    def get_dimensions_values(self, indices=None):
        """
        Returns all the metadata values of the dimensions.
        The values are assumed to be numbers.

        :returns: array_like
        """
        if not self._dimensions_values or indices is not None:
            for dimension in self.__dims.values():
                self._dimensions_values[dimension.name] = self.get_metadata_values(
                    key=dimension.name, indices=indices
                )
        return self._dimensions_values

    def compute_orientation_colorkey(self, x_dimension: int, y_dimension: int):
        x_data = numpy.linspace(-1, 1, self.__dims[x_dimension].size * SCALE_FACTOR)
        y_data = numpy.linspace(-1, 1, self.__dims[y_dimension].size * SCALE_FACTOR)
        x_mesh, y_mesh = numpy.meshgrid(x_data, y_data)

        return compute_hsv(x_mesh, y_mesh)

    def compute_orientation_dist(
        self,
        x_dimension: int,
        y_dimension: int,
        indices=None,
        third_motor: int | None = None,
    ):
        """Computes the orientation distribution"""
        if not self.__dims or self.__dims.ndim <= 1:
            return None

        if third_motor is None:
            third_motor = 0

        x_dim_size = self.__dims[x_dimension].size
        y_dim_dize = self.__dims[y_dimension].size

        ori_dist = numpy.zeros(x_dim_size * y_dim_dize)
        _slice1 = ori_dist.shape[0] * third_motor
        _slice2 = ori_dist.shape[0] * (third_motor + 1)
        ori_dist[indices] = self.get_data(indices).sum(axis=1)[_slice1:_slice2]
        return ori_dist.reshape((x_dim_size, y_dim_dize)).T

    def apply_background_subtraction(
        self,
        background=None,
        method="median",
        indices=None,
        step=None,
        chunk_shape=[100, 100],
        _dir=None,
    ):
        """
        Applies background subtraction to the data and saves the new data
        into disk.

        :param background: Data to be used as background. If None, data with indices `indices` is used.
            If Dataset, data of the dataset is used. If array, use data with indices in the array.
        :type background: Union[None, array_like, Dataset]
        :param method: Method to use to compute the background.
        :type method: Method
        :param indices: Indices of the images to apply background subtraction.
            If None, the background subtraction is applied to all the data.
        :type indices: Union[None, array_like]
        :param int step: Distance between images to be used when computing the median.
            Parameter used only when flag in_memory is False and method is `Method.median`.
            If `step` is not None, all images with distance of `step`, starting at 0,
            will be loaded into memory for computing the median, if the data loading throws
            a MemoryError, the median computation is tried with `step += 1`.
        :param chunk_shape: Shape of the chunk image to use per iteration.
            Parameter used only when flag in_memory is False and method is `Method.median`.
        :type chunk_shape: array_like
        :returns: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        :rtype: Dataset
        """

        _dir = self.dir if _dir is None else _dir

        os.makedirs(_dir, exist_ok=True)

        temp_dir = os.path.join(_dir, "temp_dir")

        os.makedirs(temp_dir, exist_ok=True)

        method = Method.from_value(method)

        self.running_data = self.get_data(indices)

        with self.state_of_operations.run_context(Operation.BS):
            if background is None:
                bg_data = self.running_data
                if indices is None:
                    _logger.info(
                        "Computing background from %s of raw data", method.name
                    )
                else:
                    _logger.info(
                        "Computing background from %s of high intensity data",
                        method.name,
                    )
            elif isinstance(background, ImageDataset):
                bg_data = background.data
                _logger.info(
                    "Computing background from %s of `background` set", method.name
                )
            else:
                bg_data = self.get_data(background)
                _logger.info(
                    "Computing background from %s of low intensity data", method.name
                )

            if self._in_memory:
                new_data = background_subtraction(
                    self.running_data, bg_data, method
                ).view(Data)
                new_data.save(os.path.join(temp_dir, "data.hdf5"))
                urls = new_data.urls
            else:
                bg = numpy.zeros(self.running_data[0].shape, self.running_data.dtype)
                if method == Method.mean:
                    if bg_data.in_memory:
                        numpy.mean(bg_data, out=bg, axis=0)
                    else:
                        io_utils.advancement_display(
                            0, len(bg_data), "Computing mean image"
                        )
                        for i in range(len(bg_data)):
                            if not self.state_of_operations.is_running(Operation.BS):
                                return
                            bg = img2img_mean(bg_data[i], bg, i)
                            io_utils.advancement_display(
                                i + 1, len(bg_data), "Computing mean image"
                            )
                elif method == Method.median:
                    if bg_data.in_memory:
                        numpy.median(bg_data, out=bg, axis=0)
                    else:
                        if step is not None:
                            bg_indices = numpy.arange(0, len(bg_data), step)
                            try:
                                numpy.median(
                                    Data(
                                        bg_data.urls[bg_indices],
                                        bg_data.metadata[bg_indices],
                                    ),
                                    out=bg,
                                    axis=0,
                                )
                            except MemoryError:
                                if not self.state_of_operations.is_running(
                                    Operation.BS
                                ):
                                    return
                                _logger.error(
                                    "MemoryError, trying with step %s", step + 1
                                )
                                return self.apply_background_subtraction(
                                    background, method, indices, step + 1
                                )
                        else:
                            start = [0, 0]
                            img = self.running_data[0]
                            bg = numpy.empty(img.shape, img.dtype)
                            chunks_1 = int(numpy.ceil(img.shape[0] / chunk_shape[0]))
                            chunks_2 = int(numpy.ceil(img.shape[1] / chunk_shape[1]))
                            io_utils.advancement_display(
                                0,
                                chunks_1 * chunks_2 * len(bg_data),
                                "Computing median image",
                            )
                            for i in range(chunks_1):
                                for j in range(chunks_2):
                                    if not self.state_of_operations.is_running(
                                        Operation.BS
                                    ):
                                        return
                                    c_images = []
                                    cpus = multiprocessing.cpu_count()
                                    with Pool(cpus - 1) as p:
                                        c_images = p.map(
                                            partial(chunk_image, start, chunk_shape),
                                            bg_data,
                                        )
                                    io_utils.advancement_display(
                                        i * chunks_2 + j + 1,
                                        chunks_1 * chunks_2,
                                        "Computing median image",
                                    )
                                    numpy.median(
                                        c_images,
                                        out=bg[
                                            start[0] : start[0] + chunk_shape[0],
                                            start[1] : start[1] + chunk_shape[1],
                                        ],
                                        axis=0,
                                    )
                                    start[1] = chunk_shape[1] * (j + 1)
                                start[0] = chunk_shape[0] * (i + 1)
                                start[1] = 0

                if not self.state_of_operations.is_running(Operation.BS):
                    return
                urls = self.running_data.apply_funcs(
                    [(background_subtraction_2D, [bg])],
                    save=os.path.join(temp_dir, "data.hdf5"),
                    text="Applying background subtraction",
                    operation=Operation.BS,
                )
                if urls is None:
                    return

        # Set urls as shape and dimension of original urls.
        if indices is not None:
            new_urls = numpy.array(self.get_data().urls, dtype=object)
            new_urls[indices] = urls
            new_data = Data(
                new_urls.reshape(self.data.urls.shape),
                self.data.metadata,
                self._in_memory,
            )
        else:
            new_data = Data(
                urls.reshape(self.data.urls.shape), self.data.metadata, self._in_memory
            )

        new_data.save(os.path.join(_dir, "data.hdf5"), indices=indices)

        try:
            os.remove(os.path.join(temp_dir, "data.hdf5"))
            os.rmdir(temp_dir)
        except OSError as e:
            _logger.warning("Error: %s" % (e.strerror))

        return ImageDataset(
            _dir=_dir,
            data=new_data,
            dims=self.__dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def apply_hot_pixel_removal(self, kernel=3, indices=None, _dir=None):
        """
        Applies hot pixel removal to Data, and saves the new data
        into disk.

        :param int kernel: size of the kernel used to find the hot
            pixels.
        :param indices: Indices of the images to apply background subtraction.
            If None, the hot pixel removal is applied to all the data.
        :type indices: Union[None, array_like]
        :return: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        :rtype: Dataset
        """

        self.running_data = self.get_data(indices)

        _dir = self.dir if _dir is None else _dir

        os.makedirs(_dir, exist_ok=True)

        temp_dir = os.path.join(_dir, "temp_dir")

        os.makedirs(temp_dir, exist_ok=True)

        if self._in_memory:
            new_data = hot_pixel_removal_3D(self.running_data, kernel).view(Data)
            new_data.save(os.path.join(temp_dir, "data.hdf5"))
            urls = new_data.urls
        else:
            urls = self.running_data.apply_funcs(
                [(hot_pixel_removal_2D, [kernel])],
                save=os.path.join(temp_dir, "data.hdf5"),
                text="Applying hot pixel removal",
                operation=Operation.HP,
            )
            if urls is None:
                return

        if indices is not None:
            new_urls = numpy.array(self.get_data().urls, dtype=object)
            new_urls[indices] = urls
            new_data = Data(
                new_urls.reshape(self.data.urls.shape),
                self.data.metadata,
                self._in_memory,
            )
        else:
            new_data = Data(
                urls.reshape(self.data.urls.shape), self.data.metadata, self._in_memory
            )

        new_data.save(os.path.join(_dir, "data.hdf5"), indices=indices)
        try:
            os.remove(os.path.join(temp_dir, "data.hdf5"))
            os.rmdir(temp_dir)
        except OSError as e:
            _logger.warning("Error: %s" % (e.strerror))

        return ImageDataset(
            _dir=_dir,
            data=new_data,
            dims=self.__dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def apply_threshold_removal(self, bottom=None, top=None, indices=None, _dir=None):
        """
        Applies bottom threshold to Data, and saves the new data
        into disk.

        :param int bottom: bottom threshold to apply.
        :param int top: top threshold to apply.
        :param indices: Indices of the images to apply background subtraction.
            If None, the hot pixel removal is applied to all the data.
        :type indices: Union[None, array_like]
        :return: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        :rtype: Dataset
        """

        self.running_data = self.get_data(indices)

        _dir = self.dir if _dir is None else _dir

        os.makedirs(_dir, exist_ok=True)

        temp_dir = os.path.join(_dir, "temp_dir")

        os.makedirs(temp_dir, exist_ok=True)

        if self._in_memory:
            new_data = threshold_removal(self.running_data, bottom, top).view(Data)
            new_data.save(os.path.join(temp_dir, "data.hdf5"))
            urls = new_data.urls
        else:
            urls = self.running_data.apply_funcs(
                [(threshold_removal, [bottom, top])],
                save=os.path.join(temp_dir, "data.hdf5"),
                text="Applying threshold",
                operation=Operation.THRESHOLD,
            )
            if urls is None:
                return
        if indices is not None:
            new_urls = numpy.array(self.get_data().urls, dtype=object)
            new_urls[indices] = urls
            new_data = Data(
                new_urls.reshape(self.data.urls.shape),
                self.data.metadata,
                self._in_memory,
            )
        else:
            new_data = Data(
                urls.reshape(self.data.urls.shape), self.data.metadata, self._in_memory
            )

        new_data.save(os.path.join(_dir, "data.hdf5"), indices=indices)
        try:
            os.remove(os.path.join(temp_dir, "data.hdf5"))
            os.rmdir(temp_dir)
        except OSError as e:
            _logger.warning("Error: %s" % (e.strerror))

        return ImageDataset(
            _dir=_dir,
            data=new_data,
            dims=self.__dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def apply_mask_removal(self, mask: numpy.ndarray, indices=None):
        """
        Applies mask to Data, and saves the new data into disk.

        :param nd.array mask: Mask to apply with 0's on the mask.
        :param indices: Indices of the images to apply background subtraction.
            If None, the mask is applied to all the data.
        :type indices: Union[None, array_like]
        :return: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        :rtype: Dataset
        """

        if not numpy.any(mask):
            return self

        self.running_data = self.get_data(indices)

        _dir = self.dir

        os.makedirs(_dir, exist_ok=True)

        temp_dir = os.path.join(_dir, "temp_dir")

        os.makedirs(temp_dir, exist_ok=True)

        if self._in_memory:
            new_data = mask_removal(self.running_data, mask).view(Data)
            new_data.save(os.path.join(temp_dir, "data.hdf5"))
            urls = new_data.urls
        else:
            urls = self.running_data.apply_funcs(
                [(mask_removal, [mask])],
                save=os.path.join(temp_dir, "data.hdf5"),
                text="Removing mask",
                operation=Operation.MASK,
            )
            if urls is None:
                return
        if indices is not None:
            new_urls = numpy.array(self.get_data().urls, dtype=object)
            new_urls[indices] = urls
            new_data = Data(
                new_urls.reshape(self.data.urls.shape),
                self.data.metadata,
                self._in_memory,
            )
        else:
            new_data = Data(
                urls.reshape(self.data.urls.shape), self.data.metadata, self._in_memory
            )

        new_data.save(os.path.join(_dir, "data.hdf5"), indices=indices)
        try:
            os.remove(os.path.join(temp_dir, "data.hdf5"))
            os.rmdir(temp_dir)
        except OSError as e:
            _logger.warning("Error: %s" % (e.strerror))

        return ImageDataset(
            _dir=_dir,
            data=new_data,
            dims=self.__dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def apply_roi(
        self, origin=None, size=None, center=None, indices=None, roi_dir=None
    ):
        """
        Applies a region of interest to the data.

        :param origin: Origin of the roi
        :param size: [Height, Width] of the roi.
        :param center: Center of the roi
        :type origin: Union[2d vector, None]
        :type center: Union[2d vector, None]
        :type size: Union[2d vector, None]
        :param indices: Indices of the images to apply background subtraction.
            If None, the roi is applied to all the data.
        :type indices: Union[None, array_like]
        :param roi_dir: Directory path for the new dataset
        :type roi_dir: str
        :returns: dataset with data with roi applied.
            Note: To preserve consistence of shape between images, if `indices`
            is not None, only the data modified is returned.
        :rtype: Dataset
        """

        roi_dir = self.dir if roi_dir is None else roi_dir
        os.makedirs(roi_dir, exist_ok=True)

        self.running_data = self.get_data(indices)
        if self._in_memory:
            new_data = (
                apply_3D_ROI(self.running_data, origin, size, center).view(Data).copy()
            )
            new_data.save(os.path.join(roi_dir, "data.hdf5"), new_shape=new_data.shape)
        else:
            shape = numpy.append(
                [self.running_data.shape[0]],
                apply_2D_ROI(self.running_data[0], origin, size, center).shape,
            )
            urls = self.running_data.apply_funcs(
                [(apply_2D_ROI, [origin, size, center])],
                save=os.path.join(roi_dir, "data.hdf5"),
                text="Applying roi",
                operation=Operation.ROI,
                new_shape=shape,
            )
            if urls is None:
                return
            new_data = Data(urls, self.running_data.metadata, self._in_memory)

        transformation = self.transformation
        if transformation is not None:
            transformation = Transformation(
                transformation.kind,
                apply_2D_ROI(transformation.x, origin, size, center),
                apply_2D_ROI(transformation.y, origin, size, center),
                transformation.rotate,
            )

        if indices is None:
            shape = list(self.data.shape)[:-2]
            shape.append(new_data.shape[-2])
            shape.append(new_data.shape[-1])
            new_data = new_data.reshape(shape)
        return ImageDataset(
            _dir=roi_dir,
            data=new_data,
            dims=self.__dims,
            transformation=transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def find_shift(self, dimension=None, steps=50, indices=None):
        """
        Find shift of the data or part of it.

        :param dimension: Parameters with the position of the data in the reshaped
            array.
        :type dimension: Union[None, tuple, array_like]
        :param float h_max: See `core.imageRegistration.shift_detection`
        :param float h_step: See `core.imageRegistration.shift_detection`
        :param indices: Boolean index list with True in the images to apply the shift to.
            If None, the hot pixel removal is applied to all the data.
        :type indices: Union[None, array_like]
        :returns: Array with shift per frame.
        """
        data = self.get_data(indices=indices, dimension=dimension)
        return shift_detection(data, steps)

    def find_shift_along_dimension(
        self, dimension: Tuple[int, ...], steps=50, indices=None
    ):
        shift = []
        for value in range(self.dims.get(dimension[0]).size):
            shift.append(self.find_shift([dimension[0], value], steps, indices))
        return numpy.array(shift)

    def apply_shift_along_dimension(
        self,
        shift: numpy.ndarray,
        dimension: Tuple[int, ...],
        shift_approach="fft",
        indices=None,
        callback=None,
        _dir=None,
    ):
        dataset = self
        for value in range(self.dims.get(dimension[0]).size):
            data = self.get_data(indices=indices, dimension=[dimension[0], value])
            frames_indices = numpy.arange(data.shape[0])
            dataset = dataset.apply_shift(
                numpy.outer(
                    shift[value], frames_indices
                ),  # cumulative shift according to frame index
                [dimension[0], value],
                shift_approach,
                indices,
                callback,
                _dir,
            )

        return dataset

    def apply_shift(
        self,
        shift: numpy.ndarray,
        dimension=None,
        shift_approach="fft",
        indices=None,
        callback=None,
        _dir=None,
    ):
        """
        Apply shift of the data or part of it and save new data into disk.

        :param array_like shift: Shift per frame.
        :param dimension: Parametes with the position of the data in the reshaped
            array.
        :type dimension: Union[None, tuple, array_like]
        :param Union['fft', 'linear'] shift_approach: Method to use to apply the shift.
        :param indices: Boolean index list with True in the images to apply the shift to.
            If None, the hot pixel removal is applied to all the data.
        :type indices: Union[None, array_like]
        :param Union[function, None] callback: Callback
        :returns: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        """
        assert len(shift) > 0, "Shift list can't be empty"

        if not numpy.any(shift):
            return self

        _dir = self.dir if _dir is None else _dir

        os.makedirs(_dir, exist_ok=True)

        data, rindices = self.get_data(indices, dimension, return_indices=True)

        with self.state_of_operations.run_context(Operation.SHIFT):
            _file = None
            try:
                try:
                    filename = os.path.join(_dir, "data.hdf5")
                    _file = h5py.File(filename, "a")
                except OSError:
                    if os.path.exists(filename):
                        os.remove(filename)
                    _file = h5py.File(filename, "w")
                dataset_name = "dataset"
                if "dataset" not in _file:
                    _file.create_dataset(
                        "dataset", self.get_data().shape, dtype=self.data.dtype
                    )
                elif self.get_data().shape != _file["dataset"].shape:
                    del _file["dataset"]
                    _file.create_dataset(
                        "dataset", self.get_data().shape, dtype=self.data.dtype
                    )
                else:
                    dataset_name = "update_dataset"
                    _file.copy("dataset", "update_dataset")

                io_utils.advancement_display(0, len(data), "Applying shift")
                if dimension is not None:
                    # Convert dimension and value into list
                    if type(dimension[0]) is int:
                        dimension[0] = [dimension[0]]
                        dimension[1] = [dimension[1]]
                    urls = []
                    for i, idx in enumerate(rindices):
                        if not self.state_of_operations.is_running(Operation.SHIFT):
                            if "update_dataset" in _file:
                                del _file["update_dataset"]
                            return
                        img = apply_opencv_shift(data[i], shift[:, i], shift_approach)
                        if shift[:, i].all() > 1:
                            shift_approach = "linear"
                        _file[dataset_name][idx] = img
                        urls.append(
                            DataUrl(
                                file_path=_dir + "/data.hdf5",
                                data_path="/dataset",
                                data_slice=idx,
                                scheme="silx",
                            )
                        )
                        io_utils.advancement_display(
                            i + 1, len(rindices), "Applying shift"
                        )

                    # Replace specific urls that correspond to the modified data
                    new_urls = numpy.array(self.data.urls, dtype=object)
                    copy_urls = new_urls
                    if indices is not None:
                        # Create array of booleans to know which indices we have
                        bool_indices = numpy.zeros(
                            self.get_data().shape[:-2], dtype=bool
                        )
                        bool_indices[indices] = True
                        bool_indices = bool_indices.reshape(self.data.scan_shape)
                        for i, dim in enumerate(sorted(dimension[0])):
                            # Flip axis to be consistent with the data shape
                            axis = self.dims.ndim - dim - 1
                            copy_urls = numpy.swapaxes(copy_urls, 0, axis)[
                                dimension[1][i], :
                            ]
                            bool_indices = numpy.swapaxes(bool_indices, 0, axis)[
                                dimension[1][i], :
                            ]
                        copy_urls[bool_indices] = urls
                    else:
                        for i, dim in enumerate(sorted(dimension[0])):
                            # Flip axis to be consistent with the data shape
                            axis = self.dims.ndim - dim - 1
                            copy_urls = numpy.swapaxes(copy_urls, 0, axis)[
                                dimension[1][i], :
                            ]
                        copy_urls[:] = urls
                else:
                    urls = []
                    for i, idx in enumerate(rindices):
                        if not self.state_of_operations.is_running(Operation.SHIFT):
                            if "update_dataset" in _file:
                                del _file["update_dataset"]
                            return
                        if shift[:, i].all() > 1:
                            shift_approach = "linear"
                        img = apply_opencv_shift(data[i], shift[:, i], shift_approach)
                        _file[dataset_name][idx] = img
                        urls.append(
                            DataUrl(
                                file_path=_dir + "/data.hdf5",
                                data_path="/dataset",
                                data_slice=idx,
                                scheme="silx",
                            )
                        )
                        io_utils.advancement_display(i + 1, len(data), "Applying shift")
                    if indices is not None:
                        new_urls = numpy.array(self.data.urls, dtype=object).flatten()
                        numpy.put(new_urls, indices, urls)
                    else:
                        new_urls = numpy.array(urls)

                if dataset_name == "update_dataset":
                    del _file["dataset"]
                    _file["dataset"] = _file["update_dataset"]
                    del _file["update_dataset"]
            finally:
                if _file is not None:
                    _file.close()

        data = Data(
            new_urls.reshape(self.data.urls.shape),
            self.data.metadata,
            in_memory=self._in_memory,
        )
        return ImageDataset(
            _dir=_dir,
            data=data,
            dims=self.__dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

    def find_and_apply_shift(
        self,
        dimension=None,
        steps=100,
        shift_approach="fft",
        indices=None,
        callback=None,
    ):
        """
        Find the shift of the data or part of it and apply it.

        :param dimension: Parametes with the position of the data in the reshaped
            array.
        :type dimension: Union[None, tuple, array_like]
        :param float h_max: See `core.imageRegistration.shift_detection`
        :param float h_step: See `core.imageRegistration.shift_detection`
        :param Union['fft', 'linear'] shift_approach: Method to use to apply the shift.
        :param indices: Indices of the images to find and apply the shift to.
            If None, the hot pixel removal is applied to all the data.
        :type indices: Union[None, array_like]
        :param Union[function, None] callback: Callback
        :returns: Dataset with the new data.
        """
        shift = self.find_shift(dimension, steps, indices=indices)
        return self.apply_shift(shift, dimension, indices=indices)

    def _waterfall_nmf(
        self, num_components, iterations, vstep=None, hstep=None, indices=None
    ):
        """
        This method is used as a way to improve the speed of convergence of
        the NMF method. For this, it uses a waterfall model where at every step
        the output matrices serve as input for the next.
        That is, the method starts with a smaller resized images of the data,
        and computes the NMF decomposition. The next step is the same but with
        bigger images, and using as initial H and W the precomputed matrices.
        The last step is done using the actual size of the images.
        This way, the number of iterations with big images can be diminished, and
        the method converges faster.

        :param int num_components: Number of components to find.
        :param array_like iterations: Array with number of iterations per step of the waterfall.
            The size of the array sets the size of the waterfall.
        :param Union[None, array_like] indices: If not None, apply method only to indices of data.
        """

        import shutil

        from skimage.transform import resize

        W = None
        H = None
        shape = numpy.asarray(self.get_data(0).shape)
        first_size = (shape / (len(iterations) + 1)).astype(int)
        size = first_size

        os.makedirs(os.path.join(self.dir, "waterfall"), exist_ok=True)

        _logger.info("Starting waterfall NMF")

        for i in range(len(iterations)):
            new_urls = []
            if indices is None:
                indices = range(self.nframes)
            for j in indices:
                filename = os.path.join(self.dir, "waterfall", str(j) + ".npy")
                numpy.save(filename, resize(self.get_data(j), size))
                new_urls.append(DataUrl(file_path=filename, scheme="fabio"))
            data = Data(new_urls, self.get_data(indices).metadata, self._in_memory)
            dataset = ImageDataset(
                _dir=os.path.join(self.dir, "waterfall"),
                data=data,
                in_memory=self._in_memory,
            )
            if vstep:
                v_step = vstep * (len(iterations) - i)
            if hstep:
                h_step = hstep * (len(iterations) - i)
            H, W = dataset.nmf(
                num_components, iterations[i], W=W, H=H, vstep=v_step, hstep=h_step
            )
            size = first_size * (i + 2)
            H2 = numpy.empty((H.shape[0], size[0] * size[1]))
            for row in range(H.shape[0]):
                H2[row] = resize(H[row].reshape((i + 1) * first_size), size).flatten()
            H = H2

        try:
            shutil.rmtree(os.path.join(self.dir, "waterfall"))
        except Exception as e:
            print(
                "Failed to delete %s. Reason: %s"
                % (os.path.join(self.dir, "waterfall"), e)
            )

        H = resize(H, (num_components, shape[0] * shape[1]))

        return H, W

    def pca(self, num_components=None, chunk_size=500, indices=None, return_vals=False):
        """
        Compute Principal Component Analysis on the data.
        The method, first converts, if not already, the data into an hdf5 file object
        with the images flattened in the rows.

        :param num_components: Number of components to find.
            If None, it uses the minimum between the number of images and the
            number of pixels.
        :type num_components: Union[None, int]
        :param chunk_size: Number of chunks for which the whitening must be computed,
            incrementally
        :type chunksize: Union[None, int], optional
        :param indices: If not None, apply method only to indices of data, defaults to None
        :type indices: Union[None, array_like], optional
        :param return_vals: If True, returns only the singular values of PCA, else returns
            the components and the mixing matrix, defaults to False
        :type return_vals: bool, optional

        :return: (H, W): The components matrix and the mixing matrix.
        """
        bss_dir = os.path.join(self.dir, "bss")
        os.makedirs(bss_dir, exist_ok=True)
        if self._in_memory:
            from sklearn import decomposition

            model = decomposition.PCA(n_components=num_components)

            with self.data.open_as_hdf5(bss_dir) as h5dset:
                if indices is not None:
                    W = model.fit_transform(h5dset[indices])
                else:
                    W = model.fit_transform(h5dset[:, :])

            H, vals, W = model.components_, model.singular_values_, W
        else:
            with self.data.open_as_hdf5(bss_dir) as h5dset:
                model = IPCA(
                    h5dset,
                    chunk_size,
                    num_components,
                    indices=indices,
                )
                with h5py.File(os.path.join(bss_dir, "ipca.hdf5"), "w") as file:
                    file["W"] = numpy.random.random(
                        (model.num_samples, model.num_components)
                    )
                    file["H"] = numpy.random.random(
                        (model.num_components, model.num_features)
                    )
                    with warnings.catch_warnings():
                        # scikit_learn<1.1.1
                        warnings.filterwarnings(
                            "always", "Mean of empty slice.", RuntimeWarning
                        )
                        with numpy.errstate(invalid="ignore", divide="ignore"):
                            model.fit_transform(W=file["W"], H=file["H"])

            H, vals, W = model.H, model.singular_values, model.W
        return vals if return_vals else (H, W)

    def nica(
        self,
        num_components,
        chunksize=None,
        num_iter=500,
        error_step=None,
        indices=None,
    ):
        """
        Compute Non-negative Independent Component Analysis on the data.
        The method, first converts, if not already, the data into an hdf5 file object
        with the images flattened in the rows.

        :param num_components: Number of components to find
        :type num_components: Union[None, int]
        :param chunksize: Number of chunks for which the whitening must be computed,
            incrementally, defaults to None
        :type chunksize: Union[None, int], optional
        :param num_iter: Number of iterations, defaults to 500
        :type num_iter: int, optional
        :param error_step: If not None, find the error every error_step and compares it
            to check for convergence. TODO: not able for huge datasets.
        :param indices: If not None, apply method only to indices of data, defaults to None
        :type indices: Union[None, array_like], optional

        :return: (H, W): The components matrix and the mixing matrix.
        """
        bss_dir = os.path.join(self.dir, "bss")
        os.makedirs(bss_dir, exist_ok=True)

        if self._in_memory:
            chunksize = None
        with self.data.open_as_hdf5(bss_dir) as h5dest:
            model = NICA(
                h5dest,
                num_components,
                chunksize,
                indices=indices,
            )
            model.fit_transform(max_iter=num_iter, error_step=error_step)
            return numpy.abs(model.H), numpy.abs(model.W)

    def nmf(
        self,
        num_components,
        num_iter=100,
        error_step=None,
        waterfall=None,
        H=None,
        W=None,
        vstep=100,
        hstep=1000,
        indices=None,
        init=None,
    ):
        """
        Compute Non-negative Matrix Factorization on the data.
        The method, first converts, if not already, the data into an hdf5 file object
        with the images flattened in the rows.

        :param num_components: Number of components to find
        :type num_components: Union[None, int]
        :param num_iter: Number of iterations, defaults to 100
        :type num_iter: int, optional
        :param error_step: If not None, find the error every error_step and compares it
            to check for convergence, defaults to None
            TODO: not able for huge datasets.
        :type error_step: Union[None, int], optional
        :param waterfall: If not None, NMF is computed using the waterfall method.
            The parameter should be an array with the number of iterations per
            sub-computation, defaults to None
        :type waterfall: Union[None, array_like], optional
        :param H: Init matrix for H of shape (n_components, n_samples), defaults to None
        :type H: Union[None, array_like], optional
        :param W: Init matrix for W of shape (n_features, n_components), defaults to None
        :type W: Union[None, array_like], optional
        :param indices: If not None, apply method only to indices of data, defaults to None
        :type indices: Union[None, array_like], optional

        :return: (H, W): The components matrix and the mixing matrix.
        """
        bss_dir = os.path.join(self.dir, "bss")
        os.makedirs(bss_dir, exist_ok=True)

        if self._in_memory:
            from sklearn import decomposition

            model = decomposition.NMF(
                n_components=num_components, init=init, max_iter=num_iter
            )
            with self.data.open_as_hdf5(bss_dir) as h5dest:
                if indices is not None:
                    X = h5dest[indices]
                else:
                    X = h5dest
                if numpy.any(X[:, :] < 0):
                    _logger.warning("Setting negative values to 0 to compute NMF")
                    X[X[:, :] < 0] = 0
                if H is not None:
                    X = X.astype(H.dtype)
                elif W is not None:
                    X = X.astype(W.dtype)
                with warnings.catch_warnings():
                    warnings.simplefilter("always", ConvergenceWarning)
                    W = model.fit_transform(X, W=W, H=H)
                return model.components_, W
        else:
            if waterfall is not None:
                H, W = self._waterfall_nmf(
                    num_components, waterfall, vstep, hstep, indices=indices
                )

            with self.data.open_as_hdf5(bss_dir) as h5dest:
                model = NMF(h5dest, num_components, indices=indices)
                with warnings.catch_warnings():
                    warnings.simplefilter("always", ConvergenceWarning)
                    model.fit_transform(
                        max_iter=num_iter,
                        H=H,
                        W=W,
                        vstep=vstep,
                        hstep=hstep,
                        error_step=error_step,
                    )
                return model.H, model.W

    def nica_nmf(
        self,
        num_components,
        chunksize=None,
        num_iter=500,
        waterfall=None,
        error_step=None,
        vstep=100,
        hstep=1000,
        indices=None,
    ):
        """
        Applies both NICA and NMF to the data. The init H and W for NMF are the
        result of NICA.
        """
        H, W = self.nica(num_components, chunksize, num_iter, indices=indices)

        # Initial NMF factorization: X = F0 * G0
        W = numpy.abs(W)
        H = numpy.abs(H)

        return self.nmf(
            min(num_components, H.shape[0]),
            num_iter,
            error_step,
            waterfall,
            H,
            W,
            vstep,
            hstep,
            indices=indices,
            init="custom",
        )

    def apply_moments(self, indices=None, chunk_shape=(500, 500)):
        """
        Compute the COM, FWHM, skewness and kurtosis of the data for very dimension.

        :param indices: If not None, apply method only to indices of data, defaults to None
        :type indices: Union[None, array_like], optional
        :param chunk_shape: Shape of the chunk image to use per iteration.
            Parameter used only when flag in_memory is False.
        :type chunk_shape: array_like, optional
        """

        if not self.dims.ndim:
            raise NoDimensionsError("apply_moments")
        self.running_data = self.get_data(indices)
        for axis, dim in self.dims.items():
            # Get motor values per image of the stack
            values = self.get_dimensions_values(indices)[dim.name]
            if self._in_memory:
                # Data in memory
                moments = numpy.asarray(
                    compute_moments(values, self.running_data), dtype=numpy.float64
                )
            else:
                # Data on disk
                start = [0, 0]
                img = self.running_data[0]
                moments = numpy.empty(
                    (4, img.shape[0], img.shape[1]), dtype=numpy.float64
                )
                chunks_1 = int(numpy.ceil(img.shape[0] / chunk_shape[0]))
                chunks_2 = int(numpy.ceil(img.shape[1] / chunk_shape[1]))
                io_utils.advancement_display(
                    0, chunks_1 * chunks_2 * len(self.running_data), "Computing moments"
                )
                for i in range(chunks_1):
                    for j in range(chunks_2):
                        c_images = []
                        cpus = multiprocessing.cpu_count()
                        with Pool(cpus - 1) as p:
                            c_images = p.map(
                                partial(chunk_image, start, chunk_shape),
                                self.running_data,
                            )
                        io_utils.advancement_display(
                            i * chunks_2 + j + 1,
                            chunks_1 * chunks_2,
                            "Computing moments",
                        )
                        com, std, skew, kurt = compute_moments(values, c_images)
                        moments[0][
                            start[0] : start[0] + chunk_shape[0],
                            start[1] : start[1] + chunk_shape[1],
                        ] = com
                        moments[1][
                            start[0] : start[0] + chunk_shape[0],
                            start[1] : start[1] + chunk_shape[1],
                        ] = std
                        moments[2][
                            start[0] : start[0] + chunk_shape[0],
                            start[1] : start[1] + chunk_shape[1],
                        ] = skew
                        moments[3][
                            start[0] : start[0] + chunk_shape[0],
                            start[1] : start[1] + chunk_shape[1],
                        ] = kurt
                        start[1] = chunk_shape[1] * (j + 1)
                    start[0] = chunk_shape[0] * (i + 1)
                    start[1] = 0
            self.moments_dims[axis] = moments

        return self.moments_dims

    def apply_fit(
        self,
        indices=None,
        int_thresh: float | None = None,
        method: str | None = None,
        chunk_shape=(100, 100),
        _dir: str | None = None,
    ) -> Tuple[ImageDataset, numpy.ndarray]:
        """
        Fits the data around axis 0 and saves the new data into disk.

        :param indices: Indices of the images to fit.
            If None, the fit is done to all the data.
        :type indices: Union[None, array_like]
        :param int_thresh: see `mapping.fit_pixel`
        :type int_thresh: Union[None, float]
        :param chunk_shape: Shape of the chunk image to use per iteration.
            Parameter used only when flag in_memory is False.
        :type chunk_shape: array_like
        :returns: dataset with data of same size as `self.data` but with the
            modified images. The urls of the modified images are replaced with
            the new urls.
        """
        if not self.dims.ndim:
            raise NoDimensionsError("apply_fit")

        _dir = self.dir if _dir is None else _dir
        _dir = os.path.join(_dir, "fit")

        os.makedirs(_dir, exist_ok=True)

        if method is None:
            method = "trf"

        with self.state_of_operations.run_context(Operation.FIT):
            urls = []
            values = None
            shape = None
            data = self.get_data(indices)
            # Fit can only be done if rocking curves are at least of size 3
            if len(data) < 3:
                raise ValueError(
                    f"Fit can only be done if rocking curves are at least of dimensionality 3. Got {len(data)}"
                )
            if indices is None:
                indices = range(data.shape[0])

            if self.dims.ndim == 1:
                data = self.get_data(indices)
                _fit = fit_data
                if self.dims.ndim > 0:
                    values = self.get_metadata_values(
                        key=self.dims.get(0).name,
                        indices=indices,
                    )
                else:
                    values = None
                maps = numpy.empty((len(MAPS_1D), *data.frame_shape))
            elif self.dims.ndim == 2:
                xdim = self.dims.get(0)
                ydim = self.dims.get(1)
                values = [
                    self.get_metadata_values(key=xdim.name),
                    self.get_metadata_values(key=ydim.name),
                ]
                shape = [xdim.size, ydim.size]
                _fit = fit_2d_data
                data = self.get_data()
                maps = numpy.empty((len(MAPS_2D), *data.frame_shape))
            else:
                raise TooManyDimensionsForRockingCurvesError()
            if not data.in_memory:
                # Use chunks to load the data into memory
                start = [0, 0]
                chunks_1 = int(numpy.ceil(data.frame_shape[0] / chunk_shape[0]))
                chunks_2 = int(numpy.ceil(data.frame_shape[1] / chunk_shape[1]))
                img = numpy.empty(data.frame_shape)
                io_utils.advancement_display(
                    0, chunks_1 * chunks_2 * len(data), "Fitting rocking curves"
                )
                for i in range(chunks_1):
                    for j in range(chunks_2):
                        if not self.state_of_operations.is_running(Operation.FIT):
                            raise RuntimeError(
                                "Expected to be in FIT state of operation."
                            )
                        # Use multiprocessing to chunk the images
                        cpus = multiprocessing.cpu_count()
                        with Pool(cpus - 1) as p:
                            c_images = p.map(
                                partial(chunk_image, start, chunk_shape), data
                            )
                        fitted_data, chunked_maps = _fit(
                            numpy.asarray(c_images),
                            values=values,
                            shape=shape,
                            indices=indices,
                            int_thresh=int_thresh,
                            method=method,
                        )
                        for k in range(len(fitted_data)):
                            filename = os.path.join(
                                _dir, "data_fit_" + str(indices[k]).zfill(4) + ".npy"
                            )
                            if (i, j) != (0, 0):
                                # If chunk is not the first, load image from disk
                                img = numpy.load(filename)
                            else:
                                urls.append(DataUrl(file_path=filename, scheme="fabio"))
                            img[
                                start[0] : start[0] + chunk_shape[0],
                                start[1] : start[1] + chunk_shape[1],
                            ] = fitted_data[k]
                            numpy.save(filename, img)
                            io_utils.advancement_display(
                                i * chunks_2 * len(data) + j * len(data) + k + 1,
                                chunks_1 * chunks_2 * len(data),
                                "Fitting rocking curves",
                            )
                        maps[
                            :,
                            start[0] : start[0] + chunk_shape[0],
                            start[1] : start[1] + chunk_shape[1],
                        ] = chunked_maps
                        start[1] = chunk_shape[1] * (j + 1)
                    start[0] = chunk_shape[0] * (i + 1)
                    start[1] = 0
            else:
                fitted_data, maps = _fit(
                    data,
                    values=values,
                    shape=shape,
                    int_thresh=int_thresh,
                    indices=indices,
                    method=method,
                )
                for i, image in enumerate(fitted_data):
                    filename = os.path.join(
                        _dir, "data_fit" + str(indices[i]).zfill(4) + ".npy"
                    )
                    numpy.save(filename, image)
                    urls.append(DataUrl(file_path=filename, scheme="fabio"))

        if indices is not None:
            # Replace only fitted data urls
            new_urls = numpy.array(self.data.urls, dtype=object).flatten()
            numpy.put(new_urls, indices, urls)
        else:
            new_urls = numpy.array(urls)

        data = Data(
            new_urls.reshape(self.data.urls.shape),
            self.data.metadata,
            in_memory=self._in_memory,
        )  # to modify
        return (
            ImageDataset(
                _dir=_dir,
                data=data,
                dims=self.__dims,
                transformation=self.transformation,
                in_memory=self._in_memory,
                title=self.title,
            ),
            maps,
        )

    def compute_transformation(
        self,
        d: float,
        kind: Literal["magnification", "rsm"] = "magnification",
        rotate: bool = False,
        topography_orientation: int | None = None,
        center: bool = True,
    ):
        """
        Computes transformation matrix.
        Depending on the kind of transformation, computes either RSM or magnification
        axes to be used on future widgets.

        :param d: Size of the pixel
        :param kind: Transformation to apply, either 'magnification' or 'rsm'
        :param rotate: To be used only with kind='rsm', if True the images with
            transformation are rotated 90 degrees.
        :param topography: To be used only with kind='magnification', if True
            obpitch values are divided by its sine.
        """

        if not self.dims:
            raise NoDimensionsError("compute_transformation")

        H, W = self.get_data(0).shape
        self.rotate = rotate

        def get_dataset(name) -> float | numpy.array | None:
            dataset = self.get_metadata_values(name)
            if not numpy.isscalar(dataset):
                dataset = numpy.ravel(dataset)[0]
            return dataset

        mainx = get_dataset("mainx")
        if mainx is None:
            raise ValueError(
                "no 'mainx' dataset found. Unable to compute transformation"
            )

        if kind == "rsm":
            if self.dims.ndim != 1:
                raise ValueError(
                    "RSM transformation matrix computation is only for 1D datasets. Use kind='magnification' or project the dataset first."
                )
            ffz = get_dataset("ffz")
            x, y = compute_rsm(H, W, d, ffz, -mainx, rotate)
        else:
            obx = get_dataset("obx")
            obpitch = numpy.unique(get_dataset("obpitch"))
            obpitch = obpitch[len(obpitch) // 2]
            x, y = compute_magnification(
                H, W, d, obx, obpitch, -mainx, topography_orientation, center
            )
        self.transformation = Transformation(kind, x, y, rotate)

    def project_data(self, dimension: Sequence[int], indices=None, _dir=None):
        """
        Applies a projection to the data.
        The new Dataset will have the same size as the chosen dimension, where
        the data is projected on.

        :param dimension: Dimensions to project the data onto
        :type dimension: array_like
        :param indices: Indices of the images to use for the projection.
            If None, the projection is done using all data.
        :type indices: Union[None, array_like]
        :param str _dir: Directory filename to save the new data
        """

        if not self.dims:
            raise NoDimensionsError("project_data")

        _dir = self.dir if _dir is None else _dir
        os.makedirs(_dir, exist_ok=True)

        dims = AcquisitionDims()
        if len(dimension) == 1:
            axis = self.dims.ndim - dimension[0] - 1
            dim = self.dims.get(dimension[0])
            data = []
            for i in range(dim.size):
                _sum = self.zsum(indices=indices, dimension=[dimension[0], i])
                if len(_sum):
                    data += [_sum]
            dims.add_dim(0, dim)
        elif len(dimension) == 2:
            axis = int(numpy.setdiff1d(range(self.dims.ndim), dimension)[0])
            dim1 = self.dims.get(dimension[0])
            dim2 = self.dims.get(dimension[1])
            dims.add_dim(0, dim1)
            dims.add_dim(1, dim2)
            data = []
            for i in range(dim1.size):
                for j in range(dim2.size):
                    _sum = self.zsum(indices=indices, dimension=[dimension, [i, j]])
                    if len(_sum):
                        data += [_sum]
        else:
            raise ValueError("Only 1D and 2D projection is allowed")

        dim = self.dims.get(axis)
        data = numpy.array(data).view(Data)
        metadata = numpy.swapaxes(self.data.metadata, self.dims.ndim - 1, axis)
        for i in range(self.dims.ndim - len(dimension)):
            metadata = metadata[0]
        data.save(
            os.path.join(_dir, "project_" + dim.name + ".hdf5"),
            in_memory=self._in_memory,
        )
        data.metadata = metadata

        dataset = ImageDataset(
            _dir=_dir,
            data=data,
            dims=dims,
            transformation=self.transformation,
            in_memory=self._in_memory,
            title=self.title,
        )

        return dataset.reshape_data()

    def compute_rsm(
        self,
        Q: Vector3D,
        a: float,
        map_range: float,
        pixel_size: float,
        units: Literal["poulsen", "gorfman"] | None = None,
        n: Vector3D | None = None,
        map_shape: Vector3D | None = None,
        energy: float | None = None,
        transformation: Transformation | None = None,
    ):
        diffry = self.get_metadata_values("diffry")
        if transformation is None:
            transformation = self.transformation

        if transformation is None:
            raise ValueError(
                "Transformation has to be computed first using the `compute_transformation` method"
            )

        return calculate_RSM_histogram(
            data=self.get_data(),
            diffry_values=diffry,
            twotheta=transformation.y,
            eta=transformation.x,
            Q=Q,
            a=a,
            map_range=map_range,
            units=units,
            map_shape=map_shape,
            n=n,
            E=energy,
        )

    def apply_binning(self, scale, _dir=None):
        from darfix.tasks.binning import Binning  # avoid cyclic import

        _dir = self.dir if _dir is None else _dir
        task = Binning(
            inputs={
                "dataset": self,
                "output_dir": _dir,
                "scale": scale,
            }
        )
        task.run()
        return task.outputs.dataset

    def recover_weak_beam(self, n, indices=None):
        """
        Set to zero all pixels higher than n times the standard deviation across the stack dimension

        :param n: Increase or decrease the top threshold by this fixed value.
        :type n: float
        :param indices: Indices of the images to use for the filtering.
            If None, the filtering is done using all data.
        :type indices: Union[None, array_like]
        """
        std = numpy.std(self.get_data(indices).view(numpy.ndarray), axis=0)

        return self.apply_threshold_removal(top=n * std, indices=indices)

    def __deepcopy__(self, memo):
        """
        Create copy of the dataset. The data numpy array is also copied using
        deep copy. The rest of the attributes are the same.
        """
        dataset = type(self)(
            self.dir,
            data=self.data,
            dims=self.__dims,
            in_memory=self.in_memory,
            copy_files=True,
        )
        dataset.dims = copy.deepcopy(self.__dims, memo)
        return dataset


###########################################################################################################################
#
# Code below is related to abstraction between edf and hdf5 to read metadata
# TODO When a refacto will be done about IO. This code should be replaced by a class with a higher level of abstraction :
# For now we have an existing fabio class for edf and a mock for hdf5. It would be better to have an abstract class for darfix metadata
# and 2 implementation, one for edf, one for hdf5.
#
###########################################################################################################################

POSITIONER_METADATA = fabioh5.FabioReader.POSITIONER


class _HDF5MetadataReader:
    """
    Equivalent of silx.io.fabioh5.FabioReader to give access to HDF5 metadata

    FIXME: remove this class. Storage and reading of metadata has been based on EDF. This class is a work-around
    Design of handle metadata shouldn't be based on the data type but more abstracted
    """

    def __init__(self, metadata: dict) -> None:
        self._metadata = metadata

    def get_value(self, kind, name):
        return self._metadata[name]

    def get_keys(self, kind):
        if kind == POSITIONER_METADATA:
            return tuple(self._metadata.keys())
        else:
            return tuple()


def extract_metadata_keys(
    metadata: list[fabioh5.EdfFabioReader | _HDF5MetadataReader],
) -> list[str]:
    result = []
    if len(metadata) > 0:
        result = list(metadata[0].get_keys(POSITIONER_METADATA))
    return result


def extract_metadata_values(
    metadata: list[fabioh5.EdfFabioReader | _HDF5MetadataReader],
    key: str,
    missing_value=numpy.nan,
    take_previous_when_missing: bool = True,
) -> list:
    values = []
    has_missing_value = False
    kind = POSITIONER_METADATA
    for data in metadata:
        if not isinstance(data, (_HDF5MetadataReader, EdfFabioReader)):
            raise TypeError(
                f"Metadata should contain instances of {_HDF5MetadataReader} or {EdfFabioReader}. But got {type(data)}."
            )
        try:
            value = data.get_value(kind=POSITIONER_METADATA, name=key)
        except KeyError:
            has_missing_value = True
            if take_previous_when_missing and values:
                values.append(values[-1])
            else:
                values.append(missing_value)
        else:
            if not isinstance(data, _HDF5MetadataReader):
                # _HDF5MetadataReader already returns a scalar when silx FabioReader return an array of a single element
                value = value[0]
            values.append(value)
    if has_missing_value:
        if take_previous_when_missing:
            _logger.warning(
                "Missing value(s) filled to previous value for kind '%s' and key '%s'",
                kind,
                key,
            )
        else:
            _logger.warning(
                "Missing value(s) filled with %s for kind '%s' and key '%s'",
                missing_value,
                kind,
                key,
            )
    return values


def extract_positioners(positioners: h5py.Group) -> Dict[str, h5py.Dataset]:
    # Some positioners are detectors and therefore scalars in `positioners`.
    # To detect those we need to check whether the positioner has a group
    # in the instrument group.
    instrument = positioners.parent
    instrument_names = list(instrument)
    datasets = dict()

    for name in positioners:
        dset = None

        if name in instrument_names:
            group = instrument[name]
            NX_class = group.attrs.get("NX_class", None)
            try:
                if NX_class == "NXpositioner":
                    dset = group["value"]
                elif NX_class == "NXdetector":
                    dset = group["data"]
            except KeyError:
                pass

        if dset is None:
            dset = positioners[name]

        if isinstance(dset, h5py.Dataset):
            if (
                dset.ndim == 0
                and name in ImageDataset._DATASETS_USED_FOR_TRANSFORMATION
            ) or (dset.ndim == 1):
                datasets[name] = h5py_read_dataset(dset)
    return datasets
