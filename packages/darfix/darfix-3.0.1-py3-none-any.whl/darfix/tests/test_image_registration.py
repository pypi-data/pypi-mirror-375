import numpy
import pytest

try:
    import scipy
except ImportError:
    scipy = None

from darfix.core import imageRegistration
from darfix.tests import utils


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
def rstate():
    return numpy.random.RandomState(1000)


@pytest.fixture
def header():
    counter_mne = "a b c d e f g h"
    motor_mne = "x y z k h m n"
    # Create headers
    header = []
    # Dimensions for reshaping
    rstate = numpy.random.RandomState(seed=1000)
    first_dim = rstate.rand(5)
    second_dim = rstate.rand(2)
    motors = rstate.rand(7)
    for i in numpy.arange(10):
        header.append({})
        header[i]["HeaderID"] = i
        header[i]["counter_mne"] = counter_mne
        header[i]["motor_mne"] = motor_mne
        header[i]["counter_pos"] = ""
        header[i]["motor_pos"] = ""
        for c in counter_mne:
            header[i]["counter_pos"] += str(rstate.rand(1)[0]) + " "
        for j, m in enumerate(motor_mne.split()):
            if m == "z":
                header[i]["motor_pos"] += str(first_dim[i % 5]) + " "
            elif m == "m":
                header[i]["motor_pos"] += str(second_dim[int(i > 4)]) + " "
            else:
                header[i]["motor_pos"] += str(motors[j]) + " "
    return header


@pytest.fixture
def first_frame(rstate):
    first_frame = numpy.zeros((100, 100))
    first_frame[30:40, 30:40] = rstate.randint(50, 100, size=(10, 10))

    return first_frame


def test_find_shift(data):
    """Tests the shift found"""
    shift = (-1.4, 1.32)
    for img in data:
        # The shift corresponds to the pixel offset relative to the reference image
        offset_image = imageRegistration._opencv_fft_shift(img, shift[1], shift[0])
        computed_shift = imageRegistration.find_shift(img, offset_image, 100)
        numpy.testing.assert_allclose(shift, -computed_shift, rtol=1e-04)


def test_apply_shift(data):
    """Tests the correct apply of the shift"""
    shift = (0, 0)
    for img in data:
        shifted_image = imageRegistration.apply_opencv_shift(img, shift)
        numpy.testing.assert_allclose(img, shifted_image, rtol=1e-04)
    for img in data:
        shifted_image = imageRegistration.apply_opencv_shift(
            img, shift, shift_approach="linear"
        )
        numpy.testing.assert_allclose(img, shifted_image, rtol=1e-04)


def test_improve_shift(data):
    """Tests the shift improvement"""
    h = imageRegistration.improve_linear_shift(
        data, [1, 1], 0.1, 0.1, 1, shift_approach="fft"
    )
    numpy.testing.assert_allclose(h, 0.0)
    h = imageRegistration.improve_linear_shift(
        data, [1, 1], 0.1, 0.1, 1, shift_approach="linear"
    )
    numpy.testing.assert_allclose(h, 0.0)


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection10(rstate):
    """Tests the shift detection with tolerance of 3 decimals"""
    first_frame = numpy.zeros((100, 100))
    # Simulating a series of frame with information in the middle.
    first_frame[25:75, 25:75] = rstate.randint(50, 300, size=(50, 50))
    data = [first_frame]
    shift = [1.0, 0]
    for i in range(9):
        data += [
            numpy.fft.ifftn(
                scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
            ).real
        ]
    data = numpy.asanyarray(data, dtype=numpy.int16)
    optimal_shift = imageRegistration.shift_detection(data, 100, shift_approach="fft")

    shift = [
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift))


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection01(rstate):
    """Tests the shift detection with tolerance of 5 decimals"""
    # Create a frame and repeat it shifting it every time
    first_frame = numpy.zeros((100, 100))
    first_frame[25:75, 25:75] = rstate.randint(50, 300, size=(50, 50))
    data = [first_frame]
    shift = [0, 1]
    for i in range(9):
        data += [
            numpy.fft.ifftn(
                scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
            ).real
        ]
    data = numpy.asanyarray(data, dtype=numpy.int16)
    optimal_shift = imageRegistration.shift_detection(data, 100, shift_approach="fft")

    shift = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9],
    ]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift))


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection11(rstate):
    """Tests the shift detection with tolerance of 2 decimals"""
    # Create a frame and repeat it shifting it every time
    first_frame = numpy.zeros((100, 100))
    first_frame[25:75, 25:75] = rstate.randint(50, 300, size=(50, 50))
    data = [first_frame]
    shift = [1, 1]
    for i in range(9):
        data += [
            numpy.fft.ifftn(
                scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
            ).real
        ]
    data = numpy.asanyarray(data, dtype=numpy.int16)

    optimal_shift = imageRegistration.shift_detection(data, 100)

    shift = [
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9],
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9],
    ]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift))


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection_float(rstate):
    """Tests the shift detection using shifted float with tolerance of 2 decimals"""
    first_frame = numpy.zeros((100, 100))
    # Simulating a series of frame with information in the middle.
    first_frame[25:75, 25:75] = rstate.randint(50, 300, size=(50, 50))
    data = [first_frame]
    shift = [0.5, 0.2]
    for i in range(9):
        data += [
            numpy.fft.ifftn(
                scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
            ).real
        ]
    data = numpy.asanyarray(data, dtype=numpy.int16)
    optimal_shift = imageRegistration.shift_detection(data, 100)
    shift = [
        [0, -0.5, -1, -1.5, -2, -2.5, -3, -3.5, -4, -4.5],
        [0, -0.2, -0.4, -0.6, -0.8, -1, -1.2, -1.4, -1.6, -1.8],
    ]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift, 1))


def test_shift_correction00(data):
    """Tests the shift correction of a [0,0] shift."""

    data = imageRegistration.shift_correction(
        data, numpy.outer([0, 0], numpy.arange(3))
    )
    numpy.testing.assert_allclose(data, data, rtol=1e-03)


def test_shift_correction01(data):
    """Tests the shift correction of a [0,1] shift."""

    expected = numpy.array(
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
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 3],
                [1, 2, 3, 4, 5],
            ],
            [
                [8, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
        ]
    )

    new_data = imageRegistration.shift_correction(
        data, numpy.outer([1, 0], numpy.arange(3))
    )
    numpy.testing.assert_allclose(new_data, expected, rtol=1e-03)


def test_shift_correction10(data):
    """Tests the shift correction of a [1,0] shift."""

    expected = numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [3, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [5, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
                [3, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
            ],
            [
                [4, 5, 1, 2, 3],
                [4, 5, 1, 2, 3],
                [4, 5, 1, 2, 3],
                [4, 5, 8, 2, 3],
                [4, 5, 1, 2, 3],
            ],
        ]
    )

    new_data = imageRegistration.shift_correction(
        data, numpy.outer([0, 1], numpy.arange(3))
    )
    numpy.testing.assert_allclose(new_data, expected, rtol=1e-05)


def test_shift_correction11(data):
    """Tests the shift correction of a [1,1] shift."""

    expected = numpy.array(
        [
            [
                [1, 2, 3, 4, 5],
                [2, 2, 3, 4, 5],
                [3, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 5],
            ],
            [
                [5, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
                [3, 1, 2, 3, 4],
                [5, 1, 2, 3, 4],
            ],
            [
                [4, 5, 8, 2, 3],
                [4, 5, 1, 2, 3],
                [4, 5, 1, 2, 3],
                [4, 5, 1, 2, 3],
                [4, 5, 1, 2, 3],
            ],
        ]
    )
    new_data = imageRegistration.shift_correction(
        data, numpy.outer([1, 1], numpy.arange(3))
    )
    numpy.testing.assert_allclose(new_data, expected, rtol=1e-05)


def test_shift_correction_float(data):
    """Tests the shift correction of a [0.1, 0.25] shift between images."""

    expected = [
        [
            [1, 2, 3, 4, 5],
            [2, 2, 3, 4, 5],
            [3, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
            [1, 2, 3, 4, 5],
        ],
        [
            [1.2595824, 1.7349374, 3.0299857, 3.756984, 4.9321423],
            [1.3387496, 1.6893137, 3.0737815, 3.690435, 5.6077204],
            [1.0840675, 1.836086, 2.9328897, 3.904524, 3.4343739],
            [1.220753, 1.7573147, 3.008505, 3.7896245, 4.600788],
            [1.3292272, 1.6948014, 3.0685136, 3.6984396, 5.5264597],
        ],
        [
            [0.03080546, 1.01156497, 3.30827889, 3.27796478, 5.64089073],
            [2.96707199, 1.77546528, 2.90155831, 3.6526126, 5.10329182],
            [0.03080546, 1.01156497, 3.30827889, 3.27796478, 5.64089073],
            [5.90333852, 2.53936558, 2.49483774, 4.02726042, 4.56569291],
            [5.90333852, 2.53936558, 2.49483774, 4.02726042, 4.56569291],
        ],
    ]

    new_data = imageRegistration.shift_correction(
        data, numpy.outer([0.25, 0.1], numpy.arange(3))
    )
    numpy.testing.assert_allclose(new_data, expected, rtol=1e-05)


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection0(tmpdir, first_frame, header):
    """Tests the shift detection using only an axis (dimension).
    The shift is only applied to the dimension."""
    data = [first_frame]
    shift = [0.5, 0.2]
    for i in range(1, 10):
        if i < 5:
            data += [
                numpy.fft.ifftn(
                    scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
                ).real
            ]
        else:
            data += [data[-1]]
    data = numpy.asanyarray(data, dtype=numpy.int16)
    dataset = utils.createDataset(
        data=data, header=header, _dir=str(tmpdir), backend="edf"
    )

    dataset.find_dimensions()
    dataset = dataset.reshape_data()

    # Detects shift using only images where value 1 of dimension 1 is fixed
    optimal_shift = dataset.find_shift(dimension=[1, 0])

    shift = [[0, -0.5, -1, -1.5, -2], [0, -0.2, -0.4, -0.6, -0.8]]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift, 1))


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_detection1(tmpdir, first_frame, header):
    """Tests the shift detection using only an axis (dimension).
    The shift is applied to all the dataset."""
    data = [first_frame]
    shift = [0.5, 0.2]
    for i in range(1, 10):
        data += [
            numpy.fft.ifftn(
                scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
            ).real
        ]
    data = numpy.asanyarray(data, dtype=numpy.int16)
    dataset = utils.createDataset(
        data=data, header=header, _dir=str(tmpdir), backend="edf"
    )

    dataset.find_dimensions()
    dataset = dataset.reshape_data()

    # Detects shift using only images where value 1 of dimension 1 is fixed
    optimal_shift = dataset.find_shift(dimension=[0, 0])

    shift = [[0, -2.5], [0, -1]]

    numpy.testing.assert_allclose(shift, numpy.round(optimal_shift, 1))


@pytest.mark.skipif(scipy is None, reason="scipy is missing")
def test_shift_correction0(tmpdir, first_frame, header):
    """Tests the shift correction using only an axis (dimension).
    The shift is only applied to the dimension."""
    data = [first_frame]
    shift = [0.5, 0.2]
    for i in range(1, 10):
        if i < 5:
            data += [
                numpy.fft.ifftn(
                    scipy.ndimage.fourier_shift(numpy.fft.fftn(data[-1]), shift)
                ).real
            ]
        else:
            data += [data[-1]]

    data = numpy.asanyarray(data, dtype=numpy.int16)
    dataset = utils.createDataset(
        data=data, header=header, _dir=str(tmpdir), backend="edf"
    )

    dataset.find_dimensions()
    dataset = dataset.reshape_data()

    dataset = dataset.find_and_apply_shift(dimension=[1, 0])

    for frame in dataset.data.take(0, 0):
        # Check if the difference between the shifted frames and the sample frame is small enough
        assert (abs(data[0] - numpy.round(frame, 1)) < 6).all()
