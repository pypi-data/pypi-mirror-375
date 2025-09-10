import os
from copy import deepcopy

import numpy
import pytest
from ewokscore.missing_data import MISSING_DATA

from darfix import dtypes
from darfix.tasks.dimensiondefinition import DimensionDefinition
from darfix.tests.utils import createDataset


@pytest.mark.parametrize("pre_compute_dims", (True, False))
@pytest.mark.parametrize("backend", ("hdf5", "edf"))
def test_dimension_definition(tmp_path, pre_compute_dims, backend):
    output_dir = os.path.join(tmp_path, "test_dimension_definition")
    os.makedirs(output_dir, exist_ok=True)

    counter_mne = "a b c d e f g h"
    motor_mne = "obpitch y z mainx ffz m obx"
    n_frames = 20
    dims = (n_frames, 100, 100)
    # Create headers
    header = []
    # Dimensions for reshaping
    a = numpy.random.rand(2)
    b = numpy.random.rand(5)
    c = numpy.random.rand(2)
    motors = numpy.random.rand(7)
    for i in numpy.arange(n_frames):
        header.append({})
        header[i]["HeaderID"] = i
        header[i]["counter_mne"] = counter_mne
        header[i]["motor_mne"] = motor_mne
        header[i]["counter_pos"] = ""
        header[i]["motor_pos"] = ""
        for _ in counter_mne:
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
    darfix_dataset = createDataset(
        data=data, header=header, _dir=output_dir, backend=backend
    )

    if pre_compute_dims:
        darfix_dataset.find_dimensions()
        dataset_dims = deepcopy(darfix_dataset.dims)
    else:
        dataset_dims = MISSING_DATA

    dataset = dtypes.Dataset(dataset=darfix_dataset)

    task = DimensionDefinition(
        inputs={
            "dataset": dataset,
            "dims": dataset_dims,
        }
    )
    task.run()
    assert isinstance(task.outputs.dataset, dtypes.Dataset)
    assert len(task.outputs.dataset.dataset.dims) == 3
    assert task.outputs.dataset.dataset.dims[0].name == "m"
    assert task.outputs.dataset.dataset.dims[1].name == "z"
    assert task.outputs.dataset.dataset.dims[2].name == "obpitch"
