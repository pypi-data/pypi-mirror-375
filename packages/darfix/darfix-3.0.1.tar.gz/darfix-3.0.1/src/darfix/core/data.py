from __future__ import annotations

import os
from contextlib import contextmanager
from enum import IntEnum
from typing import Generator
from typing import Optional
from typing import Tuple
from typing import Union

import h5py
import numpy
from silx.io import utils
from silx.io.url import DataUrl

from darfix.io import utils as io_utils
from darfix.io.hdf5 import hdf5_file_cache
from darfix.io.progress import display_progress


class Operation(IntEnum):
    """
    Flags for different operations in Dataset
    """

    PARTITION = 0
    BS = 1
    HP = 2
    THRESHOLD = 3
    SHIFT = 4
    ROI = 5
    MOMENTS = 6
    FIT = 7
    BINNING = 8
    MASK = 9


class StateOfOperations:
    def __init__(self):
        self._is_running = [False] * len(Operation)

    def _start(self, operation: Optional[Operation]) -> None:
        if operation is None:
            return
        self._is_running[operation] = True

    def stop(self, operation: Optional[Operation]) -> None:
        if operation is None:
            return
        self._is_running[operation] = False

    @contextmanager
    def run_context(self, operation: Optional[Operation]):
        self._start(operation)
        try:
            yield
        finally:
            self.stop(operation)

    def is_running(self, operation: Operation) -> bool:
        return self._is_running[operation]


class Data(numpy.ndarray):
    """

    Class to structure the data and link every image with its corresponding url and
    metadata. It inherits from numpy.ndarray and Overrides the necessary methods,
    taking into account the `in_memory` attribute.

    :param urls: Array with the urls of the data
    :type urls: array_like
    :param metadata: Array with the metadata of the data
    :type metadata: array_like
    :param in_memory: If True, the data is loaded into memory, default True
    :type in_memory: bool, optional
    """

    def __new__(cls, urls, metadata, in_memory=True, data=None):
        urls = numpy.asarray(urls)
        img_shape = None
        if in_memory:
            with hdf5_file_cache() as hdf5_cache:
                if data is not None and urls.shape != data.shape[:-2]:
                    data = None
                if data is None:
                    url_shape = urls.shape
                    url_idxs = numpy.unravel_index(numpy.arange(urls.size), url_shape)
                    if urls.size == 0:
                        data = numpy.empty(url_shape + (0, 0))
                    else:
                        img = hdf5_cache.get_data(next(urls.flat))
                        data = numpy.empty(url_shape + img.shape, img.dtype)
                        for url, *url_idx in zip(
                            display_progress(urls.flat, desc="Loading data in memory"),
                            *url_idxs,
                        ):
                            data[tuple(url_idx)] = hdf5_cache.get_data(url)
            obj = data.view(cls)
        else:
            # Access image one at a time using url
            obj = super().__new__(cls, urls.shape)

        obj.in_memory = in_memory
        obj.urls = urls
        obj.metadata = numpy.asarray(metadata)
        obj._file = None
        obj._img_shape = img_shape
        obj.state_of_operations = StateOfOperations()

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.urls = getattr(obj, "urls", None)
        self.metadata = getattr(obj, "metadata", None)
        self.in_memory = getattr(obj, "in_memory", None)

    def __getitem__(self, indices):
        """
        Return self[indices]
        """
        if self.in_memory:
            data = super().__getitem__(indices)
            if len(data.shape) < 3:
                data = data.view(numpy.ndarray)
            else:
                if isinstance(indices, tuple):
                    data.urls = self.urls[indices[0]]
                    data.metadata = self.metadata[indices[0]]
                else:
                    data.urls = self.urls[indices]
                    data.metadata = self.metadata[indices]
            return data
        if isinstance(indices, tuple):
            if not isinstance(self.urls[indices[0]], numpy.ndarray):
                return utils.get_data(self.urls[indices[0]])[indices[1], indices[2]]
            return Data(self.urls[indices[0]], self.metadata[indices], self.in_memory)
        if not isinstance(self.urls[indices], numpy.ndarray):
            return utils.get_data(self.urls[indices])
        return Data(self.urls[indices], self.metadata[indices], self.in_memory)

    def _iter_frames(self) -> Generator[numpy.ndarray, None, None]:
        if self.in_memory:
            fshape = (self.nframes,) + self.frame_shape
            yield from super().reshape(fshape)
        else:
            with hdf5_file_cache() as hdf5_cache:
                for url in self.urls.flatten():
                    yield hdf5_cache.get_data(url)

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super().__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + ((self.urls, self.metadata, self.in_memory),)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.urls, self.metadata, self.in_memory = state[-1]  # Set the attributes
        super().__setstate__(state[0:-1])

    def stop_operation(self, operation: Operation):
        """
        Method used for cases where threads are created to apply functions to the data.
        If method is called, the flag concerning the stop is set to 0 so that if the concerned
        operation is running in another thread it knows to stop.

        :param int operation: operation to stop
        :type int: Union[int, `Operation`]
        """
        if hasattr(self, "state_of_operations") and self.state_of_operations.is_running(
            operation
        ):
            self.state_of_operations.stop(operation)

    @property
    def shape(self) -> Tuple[int, ...]:
        """Total shape = scan shape + frame shape"""
        shape = super().shape
        if self.in_memory:
            return shape
        return shape + self.frame_shape

    @property
    def scan_shape(self) -> Tuple[int, ...]:
        return self.shape[:-2]

    @property
    def frame_shape(self) -> Tuple[int, int]:
        if self.in_memory:
            return super().shape[-2:]
        if self._img_shape is not None:
            return self._img_shape
        if self.nframes == 0:
            return 0, 0
        img_shape = utils.get_data(next(self.urls.flat)).shape
        self._img_shape = img_shape
        return img_shape

    @property
    def nframes(self) -> int:
        if self.urls is None:
            return 0
        return self.urls.size

    @property
    def ndim(self) -> int:
        """
        Number of array dimensions.
        """
        if self.in_memory:
            return super().ndim
        return super().ndim + 2

    def apply_funcs(
        self,
        funcs=[],
        indices=None,
        save=False,
        text="",
        operation=None,
        new_shape=None,
    ):
        """
        Method that applies a series of functions into the data. It can save the images
        into disk or return them.

        :param funcs: List of tupples. Every tupples contains the function to
            apply and its parameters, defaults to []
        :type funcs: array_like, optional
        :param indices: Indices of the data to apply the functions to,
            defaults to None
        :type indices: Union[None, array_like], optional
        :param save: If True, saves the images into disk, defaults to False
        :type save: bool
        :param str text: Text to show in the advancement display.
        :param int operation: operation to stop
        :type int: Union[int, `Operation`]

        :returns: Array with the new urls (if data was saved)
        """
        if indices is None:
            indices = range(len(self))
        if isinstance(indices, int):
            indices = [indices]
        urls = []
        io_utils.advancement_display(0, self.nframes, text)

        if not hasattr(self, "state_of_operations"):
            self.state_of_operations = StateOfOperations()

        with self.state_of_operations.run_context(operation):
            _file = None
            try:
                try:
                    _file = h5py.File(save, "a")
                except OSError:
                    if os.path.exists(save):
                        os.remove(save)
                    _file = h5py.File(save, "w")

                dataset_name = "dataset"
                new_shape = self.shape if new_shape is None else tuple(new_shape)
                if "dataset" in _file:
                    if new_shape != _file["dataset"].shape:
                        _file.create_dataset(
                            "update_dataset", new_shape, dtype=self.dtype
                        )
                    else:
                        _file.create_dataset(
                            "update_dataset",
                            shape=_file["dataset"].shape,
                            dtype=_file["dataset"].dtype,
                        )
                        for i, img in enumerate(_file["dataset"]):
                            _file["update_dataset"][i] = img
                    dataset_name = "update_dataset"
                else:
                    _file.create_dataset("dataset", new_shape, dtype=self.dtype)

                for i in indices:
                    if (
                        operation is not None
                        and not self.state_of_operations.is_running(operation)
                    ):
                        if "update_dataset" in _file:
                            del _file["update_dataset"]
                        return
                    #     if save:
                    #         for j in indices:
                    #             if j != i:
                    #                 filename = save + str(j).zfill(4) + ".npy"
                    #                 os.remove(filename)
                    #             else:
                    #                 break
                    #     return
                    img = self[int(i)]
                    for f, args in funcs:
                        img = f(*([img] + args))
                    if save:
                        _file[dataset_name][i] = img
                        urls.append(
                            DataUrl(
                                file_path=save,
                                data_path="/dataset",
                                data_slice=i,
                                scheme="silx",
                            )
                        )
                        # filename = save + str(i).zfill(4) + ".npy"
                        # numpy.save(filename, img)
                        # urls.append(DataUrl(file_path=filename, scheme='fabio'))
                    io_utils.advancement_display(i + 1, self.nframes, text)

                self.state_of_operations.stop(operation)

                if dataset_name == "update_dataset":
                    del _file["dataset"]
                    _file["dataset"] = _file["update_dataset"]
                    del _file["update_dataset"]
            finally:
                if _file is not None:
                    _file.close()
        return numpy.array(urls)

    def save(self, path, indices=None, new_shape=None, in_memory=True) -> None:
        """
        Save the data into `path` folder and replace Data urls.
        TODO: check if urls already exist and, if so, modify only urls[indices].

        :param path: Path to the folder
        :type path: str
        :param indices: the indices of the values to save, defaults to None
        :type indices: Union[None,array_like], optional
        """
        if not hasattr(self, "in_memory") or self.in_memory is None:
            self.in_memory = True
        urls = []

        if indices is None:
            data = self.flatten()
            indices = numpy.arange(len(data))
        else:
            data = self.flatten()[indices]

        _file = None
        try:
            try:
                _file = h5py.File(path, "a")
            except OSError:
                if os.path.exists(path):
                    os.remove(path)
                _file = h5py.File(path, "w")
            if new_shape:
                new_shape = tuple(new_shape)
            else:
                if self.ndim > 3:
                    new_shape = (self.nframes,) + self.frame_shape
                else:
                    new_shape = self.shape
            if "dataset" not in _file:
                _file.create_dataset("dataset", new_shape, dtype=self.dtype)
            elif new_shape != _file["dataset"].shape:
                del _file["dataset"]
                _file.create_dataset("dataset", new_shape, dtype=self.dtype)

            for i, j in enumerate(indices):
                _file["dataset"][j] = data[i]
                urls.append(
                    DataUrl(
                        file_path=path,
                        data_path="/dataset",
                        data_slice=j,
                        scheme="silx",
                    )
                )
            #     filename = path + str(i).zfill(4) + ".npy"
            #     numpy.save(filename, img)
            #     urls.append(DataUrl(file_path=filename, scheme='fabio'))
        finally:
            if _file is not None:
                _file.close()
        urls = numpy.asarray(urls)
        if self.urls is not None:
            new_urls = self.urls.flatten()
            new_urls[indices] = urls
            self.urls = new_urls.reshape(self.urls.shape)
        else:
            self.urls = numpy.asarray(urls)

    @contextmanager
    def open_as_hdf5(self, _dir) -> Generator[h5py.Dataset, None, None]:
        """
        Converts the data into an HDF5 file, setting flattened images in the rows.
        TODO: pass filename per parameter?

        :param _dir: Directory in which to save the HDF5 file.
        :type _dir: str

        :return: HDF5 dataset
        :rtype: `h5py.Dataset`
        """
        try:
            try:
                filename = os.path.join(_dir, "data.hdf5")
                self._file = h5py.File(filename, "a")
            except OSError:
                if os.path.exists(filename):
                    os.remove(filename)
                self._file = h5py.File(filename, "w")

            nframes = self.nframes
            frame_shape = self.frame_shape
            frame_size = frame_shape[0] * frame_shape[1]
            hdf5_shape = (nframes, frame_size)

            if "dataset" in self._file and self._file["dataset"].shape != hdf5_shape:
                del self._file["dataset"]
            if "dataset" not in self._file:
                self._file.create_dataset("dataset", shape=hdf5_shape, dtype=self.dtype)

            for image_idx, frame in enumerate(self._iter_frames()):
                self._file["dataset"][image_idx] = frame.flatten()

            yield self._file["dataset"]
        finally:
            if self._file is not None:
                self._file.close()

    def reshape(self, shape, order="C") -> "Data":
        """
        Returns an array containing the same data with a new shape of urls and metadata.
        Shape also contains image shape at the last two positions (unreshapable).

        :param shape: New shape, should be compatible with the original shape.
        :type shape: int or tuple of ints.
        :return: new Data object with urls and metadata reshaped to shape.
        """
        data = None
        if self.in_memory:
            data = super().reshape(shape, order=order).view(numpy.ndarray)
        scan_shape = shape[:-2]
        return Data(
            self.urls.reshape(scan_shape, order=order),
            self.metadata.reshape(scan_shape, order=order),
            self.in_memory,
            data=data,
        )

    def sum(self, axis=None, **kwargs) -> Union[numpy.ndarray, float]:
        """
        Sum of array elements over a given axis.

        :param axis: Only axis accepted are 0 or 1.
            With 0, the sum is done around the z axis, so a resulting image is returned.
            With 1, every images has its pixels summed and the result is a list with
            the intensity of each image.
            With None, a float is the result of the sum of all the pixels and all
            the images.
        :type axis: Union[None, int]

        :return: Summed data
        :rtype: Union[float, list]
        """
        data = self.flatten()
        if self.in_memory:
            if axis == 0:
                return super(Data, data).sum(axis=axis).view(numpy.ndarray)
            if axis == 1:
                return super(Data, data).view(numpy.ndarray).sum(axis=1).sum(axis=1)
            if axis is None:
                return super(Data, data).sum()
            raise TypeError("Axis must be None, 0 or 1")
        if axis == 0:
            if data.size == 0:
                return numpy.array([])
            if not data.shape[0]:
                return numpy.zeros(data[0].shape)
            zsum = numpy.array(data[0], dtype=numpy.float64)
            for i in range(1, len(data)):
                zsum += data[i]
            return zsum
        if axis == 1:
            return numpy.array([i.sum() for i in data])
        if axis is None:
            img_sum = 0
            for i in data:
                img_sum += i.sum()
            return img_sum
        raise TypeError("Axis must be None, 0 or 1")

    def take(self, indices, axis=None, out=None, mode="raise") -> "Data":
        """
        Take elements from urls and metadata from an array along an axis.

        :param indices: the indices of the values to extract
        :type indices: array_like
        :param axis: the axis over which to select values, defaults to None
        :type axis: Union[N one, int], optional

        :return: Flattened data.
        :rtype: :class:`Data`
        """
        urls = numpy.take(self.urls, indices, axis, mode=mode)
        metadata = numpy.take(self.metadata, indices, axis, mode=mode)
        data = None
        if self.in_memory:
            data = super().take(indices, axis, mode=mode).view(numpy.ndarray)
        return Data(urls, metadata, self.in_memory, data=data)

    def flatten(self) -> "Data":
        """Flattens the scan dimensions, not the frame dimensions.
        TODO: this should get a different function name

        :return: new data with flattened urls and metadata (but not frames).
        :rtype: :class:`Data`
        """
        if self.nframes == 0 or self.ndim <= 3:
            return self
        data = None
        if self.in_memory:
            fshape = (self.nframes,) + self.frame_shape
            # TODO: not sure why we need the vew here:
            data = super().reshape(fshape).view(numpy.ndarray)
        return Data(
            self.urls.flatten(), self.metadata.flatten(), self.in_memory, data=data
        )
