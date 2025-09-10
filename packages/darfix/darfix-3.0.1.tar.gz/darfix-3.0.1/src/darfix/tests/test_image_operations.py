import numpy
import pytest

from darfix.core import imageOperations


@pytest.fixture
def data():
    return numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [3, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 3],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [8, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
        ]
    )


@pytest.fixture
def dark():
    return numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
        ]
    )


def test_background_subtraction(data, dark):
    """Tests background subtraction function"""
    expected = numpy.array(
        [
            [
                [0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [2, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [7, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
            ],
        ]
    )

    new_data = imageOperations.background_subtraction(data, dark)
    numpy.testing.assert_array_equal(expected, new_data)


def test_im2img_mean(dark):
    """Tests img2img_mean function"""
    bg = None
    for i in range(dark.shape[0]):
        bg = imageOperations.img2img_mean(dark[i], bg, i)

    numpy.testing.assert_array_almost_equal(dark[0], bg)


def test_chunk_image(data):
    """Tests chunk_image function"""
    start = [0, 0]
    chunk_shape = [0, 0]

    img = imageOperations.chunk_image(start, chunk_shape, data[0])

    assert img.size == 0

    chunk_shape = [2, 2]

    img = imageOperations.chunk_image(start, chunk_shape, data[0])

    numpy.testing.assert_array_equal(data[0, :2, :2], img)


def test_n_sphere_mask():
    """Tests the creation of a mask from a 3d array."""

    expected = numpy.array(
        [
            [
                [False, False, False, False, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, False, False, False, False],
            ],
            [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ],
            [
                [False, False, False, False, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, True, True, True, False],
                [False, False, False, False, False],
            ],
        ]
    )

    mask = imageOperations._create_n_sphere_mask(expected.shape, radius=2)

    numpy.testing.assert_array_equal(expected, mask)


def test_circular_mask():
    """Tests the correct creation of a circular mask"""
    expected = numpy.array(
        [
            [False, False, True, False, False],
            [False, True, True, True, False],
            [True, True, True, True, True],
            [False, True, True, True, False],
            [False, False, True, False, False],
        ]
    )

    mask = imageOperations._create_circular_mask(expected.shape, radius=2)

    numpy.testing.assert_array_equal(expected, mask)


def test_hot_pixel_removal(data):
    """Tests the hot pixel removal in stack of arrays"""
    expected = numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 4],
                [1, 2, 3, 4, 3],
                [1, 2, 3, 4, 4],
                [1, 2, 3, 4, 5],
            ],
            [
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
        ],
        dtype=numpy.float32,
    )

    new_data = imageOperations.hot_pixel_removal_3D(data)
    numpy.testing.assert_array_equal(expected, new_data)


def test_threshold_removal(data):
    """Tests the threshold of the data"""

    expected = numpy.array(
        [
            [
                [1, 2, 3, 4, 0],
                [2, 2, 3, 4, 0],
                [3, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
            ],
            [
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 3],
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
            ],
            [
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
                [0, 2, 3, 4, 0],
                [1, 2, 3, 4, 0],
            ],
        ]
    )

    new_data = imageOperations.threshold_removal(data, 1, 4)

    numpy.testing.assert_array_equal(expected, new_data)
