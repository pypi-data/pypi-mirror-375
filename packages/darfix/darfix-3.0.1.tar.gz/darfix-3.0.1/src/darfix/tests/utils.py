from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List

import fabio
import h5py
import numpy
from ewoksutils.import_utils import qualname
from silx.io.dictdump import dicttoh5
from silx.io.dictdump import dicttonx
from silx.io.url import DataUrl
from silx.resources import ExternalResources

from darfix.core.dataset import ImageDataset


@dataclass
class DatasetArgs:
    data: numpy.ndarray
    header: list


utilstest = ExternalResources(
    project="darfix",
    url_base="http://www.edna-site.org/pub/darfix/testimages",
    env_key="DATA_KEY",
    timeout=60,
)


def createHDF5Dataset(
    data: numpy.ndarray, metadata_dict: dict, output_file=None, in_memory=True
):
    if output_file is None:
        output_file = os.path.join(str(tempfile.mkdtemp()), "darfix_dataset.hdf5")
    dicttoh5(metadata_dict, output_file, h5path="1.1/instrument/positioners")
    with h5py.File(output_file, mode="a") as h5f:
        h5f["1.1/instrument/detector/data"] = data
    dataset = ImageDataset(
        _dir=os.path.dirname(output_file),
        first_filename=DataUrl(
            file_path=output_file,
            data_path="1.1/instrument/detector/data",
            scheme="silx",
        ),
        in_memory=in_memory,
        isH5=True,
        metadata_url=DataUrl(
            file_path=output_file,
            data_path="1.1/instrument/positioners",
            scheme="silx",
        ),
    )
    return dataset


def createHDF5Dataset1D(
    data: numpy.ndarray, output_file=None, in_memory=True
) -> ImageDataset:
    """
    Creates an ImageDataset with `data` inside and a single moving motor in the associated metadata (1D)

    :param data: 3D dataset (N_motor_steps, N_pixels_x, N_pixels_y)
    :param output_file: Name of the output HDF5 file where the data will be saved. If None (default), the file will be saved in a temporary folder
    :param in_memory: defaults to True
    """
    assert data.ndim == 3

    N_frames = data.shape[0]
    metadata_dict = {"motor1": numpy.arange(N_frames)}

    return createHDF5Dataset(data, metadata_dict, output_file, in_memory)


def createHDF5Dataset2D(
    data: numpy.ndarray, output_file=None, in_memory=True
) -> ImageDataset:
    """
    Creates an ImageDataset with `data` inside and a two moving motors in the associated metadata (2D)

    :param data: 4D dataset (N_motor1_steps, N_motor2_steps N_pixels_x, N_pixels_y)
    :param output_file: Name of the output HDF5 file where the data will be saved. If None (default), the file will be saved in a temporary folder
    :param in_memory: defaults to True
    """
    assert data.ndim == 4

    N_motor1 = data.shape[0]
    N_motor2 = data.shape[1]
    N_frames = N_motor1 * N_motor2
    motor_1 = numpy.empty((N_motor1, N_motor2))
    motor_2 = numpy.empty((N_motor1, N_motor2))
    for i in range(N_motor1):
        motor_1[i] = numpy.arange(N_motor2)
    for j in range(N_motor2):
        motor_2[:, j] = numpy.arange(N_motor1)
    metadata_dict = {"motor1": motor_1.flatten(), "motor2": motor_2.flatten()}

    data = data.reshape((N_frames, *data.shape[2:]))

    return createHDF5Dataset(data, metadata_dict, output_file, in_memory)


def createRandomEDFDataset(
    dims, nb_data_files=20, header=False, _dir=None, in_memory=True, num_dims=3
):
    """Simple creation of a dataset in _dir with the requested number of data
    files and dark files.

    :param tuple of int dims: dimensions of the files.
    :param int nb_data_files: Number of data files to create.
    :param bool header: If True, a random header is created for every frame.
    :param str or None _dir: Directory to save the temporary files.

    :return :class:`Dataset`: generated instance of :class:`Dataset`
    """
    if not isinstance(dims, tuple) and len(dims) == 2:
        raise TypeError("dims should be a tuple of two elements")
    if not isinstance(nb_data_files, int):
        raise TypeError(
            f"nb_data_files ({nb_data_files}) should be an int. Get {type(nb_data_files)} instead"
        )
    if not isinstance(_dir, (type(None), str)):
        raise TypeError(f"_dir shuld be none or a string. Get {type(_dir)} instead")

    if _dir is None:
        _dir = tempfile.mkdtemp()

    if os.path.isdir(_dir) is False:
        raise ValueError("%s is not a directory" % _dir)

    if header:
        counter_mne = "a b c d e f g h"
        motor_mne = "obpitch y z mainx ffz m obx"
        # Create headers
        header = []
        # Dimensions for reshaping
        a = sorted(numpy.random.rand(2))
        b = [numpy.random.rand()] * numpy.array([1, 1.2, 1.4, 1.6, 1.8])
        c = sorted(numpy.random.rand(2))
        motors = numpy.random.rand(7)
        for i in numpy.arange(nb_data_files):
            header.append({})
            header[i]["HeaderID"] = i
            header[i]["counter_mne"] = counter_mne
            header[i]["motor_mne"] = motor_mne
            header[i]["counter_pos"] = ""
            header[i]["motor_pos"] = ""
            for count in counter_mne:
                header[i]["counter_pos"] += str(numpy.random.rand(1)[0]) + " "
            for j, m in enumerate(motor_mne.split()):
                if m == "m":
                    header[i]["motor_pos"] += str(b[i % 5]) + " "
                elif m == "z" and num_dims > 1:
                    header[i]["motor_pos"] += (
                        str(a[int((i > 4 and i < 10) or i > 14)]) + " "
                    )
                elif m == "obpitch" and num_dims == 3:
                    header[i]["motor_pos"] += str(c[int(i > 9)]) + " "
                else:
                    header[i]["motor_pos"] += str(motors[j]) + " "

            data_file = os.path.join(_dir, "data_file%04i.edf" % i)
            image = fabio.edfimage.EdfImage(
                data=numpy.random.random(dims), header=header[i]
            )
            image.write(data_file)
    else:
        for index in range(nb_data_files):
            data_file = os.path.join(_dir, "data_file%04i.edf" % index)
            image = fabio.edfimage.EdfImage(data=numpy.random.random(dims))
            image.write(data_file)

    dataset = ImageDataset(_dir=_dir, in_memory=in_memory)
    return dataset


def createRandomHDF5Dataset(
    dims,
    nb_data_frames=20,
    output_file=None,
    in_memory=True,
    num_dims=3,
    metadata=False,
):
    """Simple creation of a dataset in output_file with the requested number of data
    files and dark files.

    :param tuple of int dims: dimensions of the files.
    :param int nb_data_frames: Number of data files to create.
    :param str or None output_file: output HDF5 file
    :param in_memory: if True load the Dataset in memory
    :param int num_dims: number of dimensions of the dataset

    :return :class:`Dataset`: generated instance of :class:`Dataset`
    """
    if not isinstance(dims, tuple) and len(dims) == 2:
        raise TypeError("dims should be a tuple of two elements")
    if not isinstance(nb_data_frames, int):
        raise TypeError(
            f"nb_data_frames ({nb_data_frames}) should be an int. Get {type(nb_data_frames)} instead"
        )
    if not isinstance(output_file, (type(None), str)):
        raise TypeError(
            f"output_file shuld be none or a string. Get {type(output_file)} instead"
        )

    if output_file is None:
        output_file = os.path.join(str(tempfile.mkdtemp()), "darfix_dataset.hdf5")

    metadata_dict = {}
    if metadata:
        metadata_dict["obx"] = [numpy.random.rand(1)[0]] * nb_data_frames
        metadata_dict["mainx"] = [numpy.random.rand(1)[0]] * nb_data_frames
        metadata_dict["ffz"] = [numpy.random.rand(1)[0]] * nb_data_frames
        metadata_dict["y"] = [numpy.random.rand(1)[0]] * nb_data_frames

        # comes from createRandomEDFDataset. Don't know why those
        # values are making sense...
        a = sorted(numpy.random.rand(2))
        b = [numpy.random.rand()] * numpy.array([1, 1.2, 1.4, 1.6, 1.8])
        c = sorted(numpy.random.rand(2))
        metadata_dict["m"] = [b[i % 5] for i in range(nb_data_frames)]
        if num_dims > 1:
            metadata_dict["z"] = [
                a[int((i > 4 and i < 10) or i > 14)] for i in range(nb_data_frames)
            ]
        metadata_dict["obpitch"] = [c[int(i > 9)] for i in range(nb_data_frames)]

    data = numpy.random.random((nb_data_frames, *dims))
    dicttoh5(metadata_dict, output_file, h5path="1.1/instrument/positioners")
    with h5py.File(output_file, mode="a") as h5f:
        h5f["1.1/instrument/detector/data"] = data
    assert os.path.exists(output_file)

    dataset = ImageDataset(
        _dir=os.path.dirname(output_file),
        first_filename=DataUrl(
            file_path=output_file,
            data_path="1.1/instrument/detector/data",
            scheme="silx",
        ),
        in_memory=in_memory,
        isH5=True,
        metadata_url=DataUrl(
            file_path=output_file,
            data_path="1.1/instrument/positioners",
            scheme="silx",
        ),
    )
    return dataset


def createDataset(
    data, filter_data=False, header=None, _dir=None, in_memory=True, backend="hdf5"
):
    """
    Create a dataset from a configuration

    :param numpy.ndarray data: Images to form the data.
    :param numpy.ndarray dark_frames: Images to form the dark frames.
    :param bool filter_data: If True, the dataset created will divide the data
        between the ones with no intensity (or very low) and the others.
    :param Union[None,array_like] header: List with a header per frame. If None,
        no header is added.
    :param str or None _dir: Directory to save the temporary files.
    :param str backend: can be 'edf' or 'hdf5' according to the data format we want to save the dataset to

    :return :class:`Dataset`: generated instance of :class:`Dataset`.
    """
    assert type(_dir) in (type(None), str)
    assert len(data) > 0
    if header is not None:
        assert len(header) == len(data)

    if _dir is None:
        _dir = tempfile.mkdtemp()

    if backend == "hdf5":
        # handle HDF5 backend
        file_path = os.path.join(_dir, "darfix_dataset.hdf5")
        if header:
            metadata = {}

            def append_to_dict(key, value):
                if key not in metadata:
                    metadata[key] = [
                        value,
                    ]
                else:
                    metadata[key].append(value)

            for header_i in header:
                [
                    append_to_dict(key, float(value))
                    for key, value in zip(
                        header_i["motor_mne"].split(" "),
                        header_i["motor_pos"].split(" "),
                    )
                ]
            positioners_path = "1.1/instrument/positioners"
            dicttoh5(metadata, h5file=file_path, h5path=positioners_path, mode="a")
            metadata_url = DataUrl(
                file_path=file_path,
                data_path=positioners_path,
                scheme="silx",
            )
        else:
            metadata_url = None

        with h5py.File(file_path, mode="a") as h5f:
            h5f["1.1/instrument/detector/data"] = data

        dataset = ImageDataset(
            _dir=os.path.dirname(file_path),
            first_filename=DataUrl(
                file_path=file_path,
                data_path="1.1/instrument/detector/data",
                scheme="silx",
            ),
            in_memory=in_memory,
            isH5=True,
            metadata_url=metadata_url,
        )
    else:
        # handle EDF backend
        if os.path.isdir(_dir) is False:
            raise ValueError("%s is not a directory" % _dir)
        for index in range(len(data)):
            data_file = os.path.join(_dir, "data_file%04i.edf" % index)
            if header is not None:
                image = fabio.edfimage.EdfImage(data=data[index], header=header[index])
            else:
                image = fabio.edfimage.EdfImage(data=data[index])

            image.write(data_file)

        dataset = ImageDataset(_dir=_dir, in_memory=in_memory)

    return dataset


def create_scans(
    file_path: str,
    n_scan: int = 3,
    detector_path=r"{scan}/measurement/my_detector",
    metadata_path=r"{scan}/instrument/positioners",
):
    """
    create 'n_scan' scans with a detector like dataset and a 'positioners' groups containing motor like datasets

    warning: one of the dataset (delta) has an incoherent number of points (2 instead of 4). This is done on purpose
    to check behavior with this use case.
    """
    raw_detector_dataset = numpy.linspace(0, 5, 100 * 100 * 4).reshape(4, 100, 100)
    positioners_metadata = {
        "alpha": 1.0,
        "beta": numpy.arange(4, dtype=numpy.float32),
        "gamma": numpy.linspace(68, 70, 4, dtype=numpy.uint8),
        "delta": numpy.arange(2, dtype=numpy.int16),
    }

    for i in range(1, n_scan + 1):
        with h5py.File(file_path, mode="a") as h5f:
            h5f[detector_path.format(scan=f"{i}.1")] = raw_detector_dataset

        dicttonx(
            positioners_metadata,
            h5file=file_path,
            h5path=metadata_path.format(scan=f"{i}.1"),
            mode="a",
        )


def generate_ewoks_task_inputs(task_class, **kwargs) -> List[Dict[str, Any]]:
    task_identifier = qualname(task_class)

    return [
        {"task_identifier": task_identifier, "name": name, "value": value}
        for name, value in kwargs.items()
    ]


N_FRAMES_DIM0 = 10


def create_1d_dataset(dir, in_memory, backend, motor1, motor2):
    n_frames = N_FRAMES_DIM0
    dims = (n_frames, 100, 100)
    data = numpy.zeros(dims, dtype=numpy.float64)

    for i in range(n_frames):
        data[i] = i

    header = []
    for i in range(N_FRAMES_DIM0):
        header.append(
            {
                "motor_mne": f"mainx {motor1} {motor2}",
                "motor_pos": f"0.5 0.2 {i}",
            }
        )

    return createDataset(
        data=data,
        header=header,
        _dir=str(dir) if dir else None,
        backend=backend,
        in_memory=in_memory,
    )


def create_dataset_for_RSM(dir, in_memory, backend):
    """Create a dataset with suitable motor names to test RSM tasks"""
    return create_1d_dataset(
        dir, in_memory=in_memory, backend=backend, motor1="ffz", motor2="diffry"
    )


def _3motors_dataset_args():
    """ "
    Creating random dataset with specific headers.
    """
    counter_mne = "a b c d e f g h"
    motor_mne = "obpitch y z mainx ffz m obx"
    dims = (20, 100, 100)
    # Create headers
    header = []
    # Dimensions for reshaping
    a = numpy.random.rand(2)
    b = numpy.random.rand(5)
    c = numpy.random.rand(2)
    motors = numpy.random.rand(7)
    for i in numpy.arange(20):
        header.append({})
        header[i]["HeaderID"] = i
        header[i]["counter_mne"] = counter_mne
        header[i]["motor_mne"] = motor_mne
        header[i]["counter_pos"] = ""
        header[i]["motor_pos"] = ""
        for count in counter_mne:
            header[i]["counter_pos"] += str(numpy.random.rand(1)[0]) + " "
        for j, m in enumerate(motor_mne.split()):
            if m == "z":
                header[i]["motor_pos"] += (
                    str(a[int((i > 4 and i < 10) or i > 14)]) + " "
                )
            elif m == "m":
                header[i]["motor_pos"] += str(b[i % 5]) + " "
            elif m == "obpitch":
                header[i]["motor_pos"] += str(c[int(i > 9)]) + " "
            elif m == "mainx":
                header[i]["motor_pos"] += "50 "
            else:
                header[i]["motor_pos"] += str(motors[j]) + " "

    data = numpy.zeros(dims)
    background = numpy.random.random(dims)
    idxs = [0, 2, 4]
    data[idxs] += background[idxs]
    return DatasetArgs(data=data, header=header)


def create_3motors_dataset(dir, in_memory, backend):
    """Create a dataset with 3 motors"""
    args = _3motors_dataset_args()
    return createDataset(
        data=args.data,
        header=args.header,
        _dir=str(dir) if dir else None,
        backend=backend,
        in_memory=in_memory,
    )
