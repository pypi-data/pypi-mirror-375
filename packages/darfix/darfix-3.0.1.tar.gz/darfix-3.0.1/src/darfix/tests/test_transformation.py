import numpy
import pytest

from darfix.core.transformation import Transformation
from darfix.core.utils import NoDimensionsError

from .utils import create_1d_dataset
from .utils import create_dataset_for_RSM


@pytest.mark.parametrize("in_memory", (True, False))
@pytest.mark.parametrize("backend", ("hdf5", "edf"))
def test_rsm_kind(tmpdir, in_memory, backend):
    dataset = create_dataset_for_RSM(dir=tmpdir, in_memory=in_memory, backend=backend)

    with pytest.raises(NoDimensionsError):
        dataset.compute_transformation(0.1, kind="rsm")
    dataset.find_dimensions()

    assert dataset.transformation is None
    dataset.compute_transformation(0.1, kind="rsm")

    transformation = dataset.transformation

    assert isinstance(transformation, Transformation)
    assert transformation.shape == dataset.get_data(0).shape
    assert numpy.all(numpy.isfinite(transformation.x))
    assert numpy.all(numpy.isfinite(transformation.y))


@pytest.mark.parametrize("in_memory", (True, False))
@pytest.mark.parametrize("backend", ("hdf5", "edf"))
def test_magnification_kind(tmpdir, in_memory, backend):
    dataset = create_1d_dataset(
        dir=tmpdir,
        in_memory=in_memory,
        backend=backend,
        motor1="obx",
        motor2="obpitch",
    )

    with pytest.raises(NoDimensionsError):
        dataset.compute_transformation(0.1, kind="magnification")
    dataset.find_dimensions()

    assert dataset.transformation is None
    dataset.compute_transformation(0.1, kind="magnification")

    transformation = dataset.transformation

    assert isinstance(transformation, Transformation)
    assert transformation.shape == dataset.get_data(0).shape
    assert numpy.all(numpy.isfinite(transformation.x))
    assert numpy.all(numpy.isfinite(transformation.y))


def test_compute_magnification(in_memory_dataset, on_disk_dataset):
    """Tests fitting data in memory"""

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    dataset.compute_transformation(d=0.1)
    assert dataset.transformation.shape == dataset.get_data(0).shape

    #  On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    dataset.compute_transformation(d=0.1)
    assert dataset.transformation.shape == dataset.get_data(0).shape
