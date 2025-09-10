import os

import numpy
import pytest
from silx.io.url import DataUrl

from darfix.core.data import Data


@pytest.fixture
def test_arrays(tmp_path):
    _dir = str(tmp_path)
    urls = []
    metadata = []
    data = []
    for i in range(10):
        url = _dir + str(i) + ".npy"
        i_data = numpy.random.rand(100, 100)
        data += [i_data]
        urls += [DataUrl(file_path=url, scheme="fabio")]
        metadata += ["No metadata"]
        numpy.save(url, i_data)

    return (
        urls,
        metadata,
        numpy.array(data),
    )


def test_create_data_in_memory(test_arrays):
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata)

    for i in range(10):
        assert data.urls[i] == urls[i]
        assert data.metadata[i] == metadata[i]

    numpy.testing.assert_array_equal(test_data, data)


def test_create_data_on_disk(test_arrays):
    urls, metadata, _ = test_arrays
    data = Data(urls=urls, metadata=metadata, in_memory=False)

    for i in range(10):
        assert data.urls[i] == urls[i]
        assert data.metadata[i] == metadata[i]


def test_get_in_memory(test_arrays):
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata)

    for i in range(10):
        numpy.testing.assert_array_equal(data[i], test_data[i])

    indices = [0, 2, 6]
    numpy.testing.assert_array_equal(data[indices], test_data[indices])


def test_get_on_disk(test_arrays):
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata, in_memory=False)

    for i in range(10):
        numpy.testing.assert_array_equal(data[i], test_data[i])

    indices = [0, 2, 6]
    for i in range(3):
        numpy.testing.assert_array_equal(data[indices][i], test_data[indices][i])


def test_get_slices_in_memory(test_arrays):
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata)

    numpy.testing.assert_array_equal(data[2:3, 50:, 50:], test_data[2:3, 50:, 50:])


def test_get_slices_on_disk(test_arrays):
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata, in_memory=False)

    for i in range(3):
        numpy.testing.assert_array_equal(data[2:5][i], test_data[2:5][i])


def test_shape_in_memory(test_arrays):
    """Tests the correct shape of the data in memory"""
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata)
    assert data.shape == test_data.shape

    urls = numpy.array(urls).reshape((5, 2))
    data = Data(urls=urls, metadata=metadata)
    assert data.shape == (5, 2, 100, 100)


def test_shape_on_disk(test_arrays):
    """Tests the correct shape of the data on disk"""
    urls, metadata, test_data = test_arrays
    data = Data(urls=urls, metadata=metadata, in_memory=False)
    assert data.shape == test_data.shape

    urls = numpy.array(urls).reshape((5, 2))
    data = Data(urls=urls, metadata=metadata, in_memory=False)
    assert data.shape == (5, 2, 100, 100)


def test_save(tmp_path):
    data = numpy.random.rand(10, 100, 100).view(Data)
    # data.in_memory = True
    data.save(os.path.join(tmp_path, "data.hdf5"))

    numpy.testing.assert_array_equal(data.shape, (10, 100, 100))


def test_save_new_shape(tmp_path):
    data = numpy.random.rand(10, 50, 50).view(Data)
    # data.in_memory = True
    data.save(os.path.join(tmp_path, "data.hdf5"), new_shape=(10, 50, 50))

    numpy.testing.assert_array_equal(data.shape, (10, 50, 50))


def test_convert_to_hdf5(test_arrays):
    urls, metadata, _ = test_arrays

    data = Data(urls=urls, metadata=metadata)
    url_dir = os.path.dirname(urls[0].file_path())
    with data.open_as_hdf5(url_dir) as dataset:
        assert dataset.shape == (10, 10000)

    data = Data(urls=urls, metadata=metadata, in_memory=False)
    with data.open_as_hdf5(url_dir) as dataset:
        assert dataset.shape == (10, 10000)


def test_reshape(test_arrays):
    urls, metadata, _ = test_arrays
    data = Data(urls=urls, metadata=metadata)
    new_data = data.reshape((2, 5, 100, 100))
    assert new_data.shape == (2, 5, 100, 100)

    data = Data(urls=urls, metadata=metadata, in_memory=False)
    new_data = data.reshape((2, 5, 100, 100))
    assert new_data.shape == (2, 5, 100, 100)


def test_take(test_arrays):
    urls, metadata, test_data = test_arrays

    data = Data(urls=urls, metadata=metadata)
    result = numpy.take(test_data, [0, 1, 2, 3], axis=0)
    new_data = data.take([0, 1, 2, 3])
    numpy.testing.assert_array_equal(new_data, result)

    data = Data(urls=urls, metadata=metadata, in_memory=False)
    new_data = data.take([0, 1, 2, 3])
    for i in range(4):
        numpy.testing.assert_array_equal(new_data[i], result[i])


def test_flatten(test_arrays):
    urls, metadata, test_data = test_arrays

    new_urls = numpy.array(urls).reshape((2, 5))

    data = Data(urls=new_urls, metadata=metadata)
    numpy.testing.assert_array_equal(test_data, data.flatten())

    data = Data(urls=new_urls, metadata=metadata, in_memory=False)
    for i in range(4):
        numpy.testing.assert_array_equal(data.flatten()[i], test_data[i])


@pytest.mark.parametrize("in_memory", (True, False), ids=["in_memory", "on_disk"])
def test_empty_data(in_memory):
    data = Data([], [], in_memory=in_memory)
    assert data.size == 0
    assert data.ndim == 3
    assert data.shape == (0, 0, 0)
    assert data.copy().tolist() == []
