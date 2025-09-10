from __future__ import annotations

from typing import Any
from typing import TypedDict

import numpy
from silx.utils.enum import Enum as _Enum

from ..dtypes import Dataset
from .data import Operation
from .dataset import ImageDataset


class BackgroundType(_Enum):
    DATA = "Data"
    UNUSED_DATA = "Unused data (after partition)"
    DARK_DATA = "Dark data"


class NoiseRemovalOperation(TypedDict):
    type: Operation
    parameters: dict[str, Any]

    def __str__(self):
        if self["type"] == Operation.BS:
            return f"Background subtraction {self['parameters']}"

        if self["type"] == Operation.HP:
            return f"Hot pixel removal: {self['parameters']}"

        if self["type"] == Operation.THRESHOLD:
            return f"Threshold removal: {self['parameters']}"

        if self["type"] == Operation.MASK:
            return "Mask removal"

        return super().__str__(self)


def apply_noise_removal_operation(dataset: Dataset, operation: NoiseRemovalOperation):
    if operation["type"] == Operation.BS:
        return apply_background_subtraction(dataset, **operation["parameters"])

    if operation["type"] == Operation.HP:
        return apply_hot_pixel_removal(dataset, **operation["parameters"])

    if operation["type"] == Operation.THRESHOLD:
        return apply_threshold_removal(dataset, **operation["parameters"])

    if operation["type"] == Operation.MASK:
        return apply_mask_removal(dataset, **operation["parameters"])

    return None


def apply_background_subtraction(
    dataset: Dataset, method=None, step=None, chunks=None, background_type=None
) -> ImageDataset | None:
    darfix_dataset = dataset.dataset

    if method is None:
        method = "median"

    if background_type is not None:
        background_type = BackgroundType.from_value(background_type)

    if background_type == BackgroundType.DARK_DATA:
        bg = dataset.bg_dataset
    elif background_type == BackgroundType.UNUSED_DATA:
        bg = dataset.bg_indices
    else:
        bg = None

    return darfix_dataset.apply_background_subtraction(
        indices=dataset.indices,
        method=method,
        background=bg,
        step=step,
        chunk_shape=chunks,
    )


def apply_hot_pixel_removal(
    dataset: Dataset, kernel_size: int | None = None
) -> ImageDataset | None:
    if kernel_size is None:
        kernel_size = 3

    return dataset.dataset.apply_hot_pixel_removal(
        indices=dataset.indices, kernel=kernel_size
    )


def apply_threshold_removal(
    dataset: Dataset, bottom: int | None = None, top: int | None = None
) -> ImageDataset | None:
    return dataset.dataset.apply_threshold_removal(
        bottom=bottom, top=top, indices=dataset.indices
    )


def apply_mask_removal(
    dataset: Dataset, mask: numpy.ndarray | None
) -> ImageDataset | None:
    if mask is None:
        return dataset.dataset

    return dataset.dataset.apply_mask_removal(mask, indices=dataset.indices)
