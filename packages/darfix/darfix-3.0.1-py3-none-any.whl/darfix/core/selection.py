from __future__ import annotations

import copy
import typing
from collections import Sequence

import numpy


class FixedDimension(typing.NamedTuple):
    """
    A data class to describe a fixed dimension. Used as a parameter for ImageStack::filter_indices().

    This is used when we want to filter the image stack by one of the dimension.

    For instance, in my dataset dimensions, i have two motors `motor_slow` and `motor_fast`

    motor_fast
    - axis = 0
    - size : 3
    - linspace : 1, 2, 3

    motor_slow
    - axis = 1
    - size : 4
    - linspace : 0.5, 1, 1.5, 2

    Let say we want images indice of my dataset only when `motor_slow` value = 1.5

    `motor_slow` axis is 1 and value 1.5 is at index 2.

    So, I can use dataset.filter_indices(FixedDimension(axis = 1, index = 2))
    """

    axis: int
    index: int

    def get_reversed_axis(self, ndim: int) -> int:
        """
        In darfix Dimension class, `axis` =  Ndim - real_data_array_axis - 1.
        This is due to legacy.
        """
        assert ndim - self.axis - 1 >= 0
        return ndim - self.axis - 1

    @staticmethod
    def from_iterable(dimension: Sequence[int | Sequence[int]]) -> FixedDimension:
        # this is not really ideal but as for now dimension type is a mess in the code i prefere do all the dirty code here
        assert len(dimension) == 2
        dim0, dim1 = dimension
        axis = dim0 if isinstance(dim0, int) else dim0[0]
        index = dim1 if isinstance(dim1, int) else dim1[0]
        return FixedDimension(axis, index)


class Selection:
    def __init__(self, input: AnySelection):
        if isinstance(input, Selection):
            self.__dict__ = copy.deepcopy(input.__dict__)
            return
        
        if isinstance(input, FixedDimension):
            self._fixed_dims = [input]
            return

        self._fixed_dims = []

        input = numpy.asarray(input)

        if input.ndim == 2:
            assert input.shape[1] == 2
            self._fixed_dims = [FixedDimension(*pair) for pair in input if len(pair)==2 else raise ValueError("Selection ")]

    def apply(array: numpy.ndarray):
        pass

    def shape():
        pass

    def size():
        pass
    @property
    def axis():
        return None
    @property
    def index():
        return None


AnySelection = typing.Union[Sequence, numpy.ndarray, FixedDimension, Selection]
