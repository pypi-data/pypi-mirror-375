import numpy
import pytest

from darfix.core import rocking_curves
from darfix.core.data import Data
from darfix.core.dataset import ImageDataset
from darfix.core.utils import NoDimensionsError

from .utils import createRandomHDF5Dataset


def test_generator():
    """Tests the correct creation of a generator without moments"""
    data = numpy.random.random(size=(3, 10, 10))
    g = rocking_curves.generator(data)

    img, moment = next(g)
    assert moment is None
    numpy.testing.assert_array_equal(img, data[:, 0, 0])


def test_generator_with_moments():
    """Tests the correct creation of a generator with moments"""
    data = numpy.random.random(size=(3, 10, 10))
    moments = numpy.ones((3, 10, 10))
    g = rocking_curves.generator(data, moments)

    img, moment = next(g)
    numpy.testing.assert_array_equal(moment, moments[:, 0, 0])
    numpy.testing.assert_array_equal(img, data[:, 0, 0])


def test_fit_rocking_curve():
    """Tests the correct fit of a rocking curve"""

    samples = numpy.random.normal(size=10000) + numpy.random.random(10000)

    y, bins = numpy.histogram(samples, bins=100)

    y_pred, pars = rocking_curves.fit_rocking_curve((y, None))
    rss = numpy.sum((y - y_pred) ** 2)
    tss = numpy.sum((y - y.mean()) ** 2)
    r2 = 1 - rss / tss

    assert r2 > 0.9
    assert len(pars) == 4


def test_fit_data():
    """Tests the new data has same shape as initial data"""
    data = numpy.random.random(size=(3, 10, 10))
    new_data, maps = rocking_curves.fit_data(data)

    assert new_data.shape == data.shape
    assert len(maps) == 4
    assert maps[0].shape == data[0].shape


@pytest.mark.parametrize("in_memory", (True, False))
def test_apply_2d_fit_hdf5_dataset(in_memory: bool):
    dataset = createRandomHDF5Dataset(
        dims=(10, 10), nb_data_frames=10, metadata=True, in_memory=in_memory
    )
    with pytest.raises(NoDimensionsError):
        fit_dataset, maps = dataset.apply_fit()
    dataset.find_dimensions()
    indices = [0, 1, 2, 3, 4]
    fit_dataset, maps = dataset.apply_fit(indices=indices)

    assert dataset.dims.ndim == 2
    assert len(maps) == 7
    assert fit_dataset.nframes == dataset.nframes
    assert fit_dataset.data.urls[0] != dataset.data.urls[0]
    numpy.testing.assert_equal(fit_dataset.data[5], dataset.data[5])


def test_apply_2d_fit_edf_dataset(in_memory_dataset, on_disk_dataset):
    """Tests the fit with dimensions and indices"""

    # In memory
    data = Data(
        urls=in_memory_dataset.get_data().urls[:10],
        metadata=in_memory_dataset.get_data().metadata[:10],
        in_memory=True,
    )
    dataset = ImageDataset(_dir=in_memory_dataset.dir, data=data)
    dataset.find_dimensions()
    dataset = dataset.reshape_data()
    new_dataset, maps = dataset.apply_fit(indices=[1, 2, 3, 4])
    assert new_dataset.data.urls[0, 0] == dataset.data.urls[0, 0]
    assert new_dataset.data.urls[0, 1] != dataset.data.urls[0, 1]
    assert len(maps) == 7
    assert maps[0].shape == in_memory_dataset.get_data(0).shape

    #  On disk
    data = Data(
        urls=on_disk_dataset.get_data().urls[:10],
        metadata=on_disk_dataset.get_data().metadata[:10],
        in_memory=False,
    )
    dataset = ImageDataset(_dir=on_disk_dataset.dir, data=data)
    dataset.find_dimensions()
    dataset = dataset.reshape_data()
    new_dataset, maps = dataset.apply_fit(indices=[1, 2, 3, 4])

    assert new_dataset.data.urls[0, 0] == dataset.data.urls[0, 0]
    assert new_dataset.data.urls[0, 1] != dataset.data.urls[0, 1]
    assert len(maps) == 7
    assert maps[0].shape == in_memory_dataset.get_data(0).shape
