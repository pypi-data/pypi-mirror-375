import pytest

from darfix.core.utils import NoDimensionsError


def test_apply_moments(in_memory_dataset, on_disk_dataset):

    with pytest.raises(NoDimensionsError):
        in_memory_dataset.apply_moments(indices=[1, 2, 3, 4])

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    moments = dataset.apply_moments(indices=[1, 2, 3, 4])
    assert moments[0][0].shape == dataset.get_data(0).shape
    assert moments[1][3].shape == dataset.get_data(0).shape

    with pytest.raises(NoDimensionsError):
        on_disk_dataset.apply_moments(indices=[1, 2, 3, 4])

    # On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    moments = dataset.apply_moments(indices=[1, 2, 3, 4])
    assert moments[0][0].shape == dataset.get_data(0).shape
    assert moments[1][3].shape == dataset.get_data(0).shape
