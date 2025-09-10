import numpy
import pytest

from .utils import create_1d_dataset


@pytest.mark.parametrize("backend", ("hdf5", "edf"))
def test_apply_mask_from_file(tmpdir, backend):
    dataset = create_1d_dataset(
        tmpdir, in_memory=False, backend=backend, motor1="diffrx", motor2="diffry"
    )
    mask_shape = dataset.data.shape[1:]
    mask = numpy.ones(mask_shape)
    mask[20:40, 20:40] = 0

    masked_dataset = dataset.apply_mask_removal(mask)
    masked_data = masked_dataset.data
    # Do the assert frame by frame since we can't slice through DataUrls
    for i in range(len(masked_data)):
        expected_data = dataset.data[i]
        expected_data[20:40, 20:40] = 0
        numpy.testing.assert_allclose(masked_data[i], expected_data)


@pytest.mark.parametrize("backend", ("hdf5", "edf"))
def test_apply_mask_from_memory(tmpdir, backend):
    dataset = create_1d_dataset(
        tmpdir, in_memory=True, backend=backend, motor1="diffrx", motor2="diffry"
    )
    mask_shape = dataset.data.shape[1:]
    mask = numpy.ones(mask_shape)
    mask[20:40, 20:40] = 0

    masked_dataset = dataset.apply_mask_removal(mask)

    expected_data = dataset.data
    expected_data[:, 20:40, 20:40] = 0
    numpy.testing.assert_allclose(masked_dataset.data, expected_data)
