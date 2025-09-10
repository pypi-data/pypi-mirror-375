import numpy


def test_zsum(in_memory_dataset, on_disk_dataset):
    indices = [1, 2, 3, 6]

    # In memory
    in_memory_dataset.find_dimensions()
    dataset = in_memory_dataset.reshape_data()
    result = numpy.sum(dataset.get_data(dimension=[0, 1], indices=indices), axis=0)
    zsum = dataset.zsum(dimension=[0, 1], indices=indices)
    numpy.testing.assert_array_equal(zsum, result)

    # On disk
    on_disk_dataset.find_dimensions()
    dataset = on_disk_dataset.reshape_data()
    zsum = dataset.zsum(dimension=[0, 1], indices=indices)
    numpy.testing.assert_array_equal(zsum, result)
