import numpy


def test_find_shift(in_memory_dataset, on_disk_dataset):
    """Tests the shift detection with dimensions and indices"""

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    indices = [1, 2, 3, 4]
    shift = dataset.find_shift(dimension=[1, 1], indices=indices)
    assert len(shift) == 0
    shift = dataset.find_shift(dimension=[0, 1], indices=indices)
    assert shift.shape == (2, 1)

    # On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    indices = [1, 2, 3, 4]
    shift = dataset.find_shift(dimension=[1, 1], indices=indices)
    assert len(shift) == 0
    shift = dataset.find_shift(dimension=[0, 1], indices=indices)
    assert shift.shape == (2, 1)


def test_apply_shift(in_memory_dataset, on_disk_dataset):
    """Tests the shift correction with dimensions and indices"""

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    new_dataset = dataset.apply_shift(
        shift=numpy.array([[0, 0.5], [0, 0.5]]),
        dimension=[0, 1],
        indices=[1, 2, 3, 4],
    )
    assert new_dataset.data.urls[0, 0, 0] == dataset.data.urls[0, 0, 0]
    assert new_dataset.data.urls[0, 0, 1] != dataset.data.urls[0, 0, 1]

    #  On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    new_dataset = dataset.apply_shift(
        shift=numpy.array([[0, 0.5], [0, 0.5]]),
        dimension=[0, 1],
        indices=[1, 2, 3, 4],
    )

    assert new_dataset.data.urls[0, 0, 0] == dataset.data.urls[0, 0, 0]
    assert new_dataset.data.urls[0, 0, 1] != dataset.data.urls[0, 0, 1]


def test_find_shift_along_dimension(in_memory_dataset, on_disk_dataset):
    """Tests the shift detection along a dimension"""

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    indices = numpy.arange(10)
    shift = dataset.find_shift_along_dimension(dimension=[1], indices=indices)
    assert shift.shape == (2, 2, 5)
    shift = dataset.find_shift_along_dimension(dimension=[0], indices=indices)
    assert shift.shape == (5, 2, 2)

    # On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    indices = numpy.arange(10)
    shift = dataset.find_shift_along_dimension(dimension=[1], indices=indices)
    assert shift.shape == (2, 2, 5)
    shift = dataset.find_shift_along_dimension(dimension=[0], indices=indices)
    assert shift.shape == (5, 2, 2)


def test_apply_shift_along_dimension(in_memory_dataset, on_disk_dataset):
    """Tests the shift correction with dimensions and indices"""

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    shift = numpy.random.random((4, 2, 2))
    new_dataset = dataset.apply_shift_along_dimension(
        shift=shift, dimension=[1], indices=[1, 2, 3, 4]
    )
    assert new_dataset.data.urls[0, 0, 0] == dataset.data.urls[0, 0, 0]
    assert new_dataset.data.urls[0, 0, 1] != dataset.data.urls[0, 0, 1]
    #  On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    shift = numpy.random.random((4, 2, 2))
    new_dataset = dataset.apply_shift_along_dimension(
        shift=shift, dimension=[1], indices=[1, 2, 3, 4]
    )

    assert new_dataset.data.urls[0, 0, 0] == dataset.data.urls[0, 0, 0]
    assert new_dataset.data.urls[0, 0, 1] != dataset.data.urls[0, 0, 1]
