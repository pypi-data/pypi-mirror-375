import numpy

from darfix import dtypes
from darfix.tasks.datapartition import DataPartition
from darfix.tests.utils import createDataset


def test_data_partition():
    dataset = dtypes.Dataset(
        dataset=createDataset(data=numpy.linspace(1, 10, 100), in_memory=True),
    )

    # test default processing
    task = DataPartition(
        inputs={
            "dataset": dataset,
        }
    )
    task.run()

    # if no filtering then indices of all frames must exist
    numpy.testing.assert_array_equal(
        task.outputs.dataset.indices,
        numpy.arange(0, 100, step=1),
    )


def test_data_partition_with_filtering():
    dataset = dtypes.Dataset(
        dataset=createDataset(data=numpy.linspace(1, 10, 100), in_memory=True),
    )

    # test filtering
    task = DataPartition(
        inputs={
            "dataset": dataset,
            "filter_bottom_bin_idx": 5,
            "filter_top_bin_idx": 45,
        },
    )
    task.run()

    # if filtering then some indices must be ignored
    assert not numpy.array_equal(
        task.outputs.dataset.indices,
        numpy.arange(0, 100, step=1),
    )
