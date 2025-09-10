from __future__ import annotations

from typing import Tuple

import numpy

from ..dtypes import Dataset
from .dataset import ImageDataset


def apply_shift(
    input_dataset: Dataset,
    shift: Tuple[float, float] | numpy.ndarray,
    dimension_idx: int | None = None,
) -> ImageDataset:
    if not isinstance(shift, numpy.ndarray):
        shift = numpy.array(shift)

    dataset = input_dataset.dataset
    indices = input_dataset.indices

    if dimension_idx is not None:
        return dataset.apply_shift_along_dimension(
            shift, dimension=(dimension_idx,), indices=indices
        )

    frames_indices = numpy.arange(dataset.get_data(indices).shape[0])
    # Cumulative shift: frame 0 shift is 0, frame 1 shift is `shift`, frame 2 shift is `2*shift`, ...
    cumulative_shift_per_frames = numpy.outer(shift, frames_indices)
    return dataset.apply_shift(cumulative_shift_per_frames, indices=indices)
