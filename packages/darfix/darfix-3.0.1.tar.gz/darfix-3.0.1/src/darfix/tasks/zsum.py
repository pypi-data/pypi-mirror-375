from __future__ import annotations

from typing import Sequence

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict

from darfix import dtypes


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: dtypes.Dataset
    """Input dataset containing a stack of images."""
    indices: Sequence[int] | MissingData = MISSING_DATA
    """Indices of the images to sum. If not provided, all images will be summed."""
    dimension: Sequence[int] | Sequence[Sequence[int]] | MissingData = MISSING_DATA
    """Dimension along which to compute the Z-sum. If not provided, all images will be summed."""


class ZSum(
    Task,
    input_model=Inputs,
    output_names=["zsum"],
):
    """Sum all images of the dataset or images at specified indices along a given dimension."""

    def run(self):
        dataset = self.inputs.dataset
        if isinstance(dataset, dtypes.Dataset):
            dataset = dataset.dataset
        if not isinstance(dataset, dtypes.ImageDataset):
            raise TypeError(
                f"dataset is expected to be an instance of {dtypes.ImageDataset}. But get {type(dataset)}"
            )

        indices = self.get_input_value("indices", None)
        dimension = self.get_input_value("dimension", None)
        self.outputs.zsum = dataset.zsum(
            indices=indices,
            dimension=dimension,
        )
