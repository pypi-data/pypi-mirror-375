from __future__ import annotations

from typing import Sequence

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict

from darfix.core.shiftcorrection import apply_shift
from darfix.dtypes import Dataset


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: Dataset
    """ Input dataset containing a stack of images """
    shift: Sequence[float] | MissingData = MISSING_DATA
    """Shift to apply to the images. If not provided, dataset will be unchanged."""
    dimension: int | MissingData = MISSING_DATA


class ShiftCorrection(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    def run(self):
        dataset: Dataset = self.inputs.dataset
        shift: Sequence[float] = self.get_input_value("shift", None)
        dimension: int | None = self.get_input_value("dimension", None)

        if shift is None:
            self.outputs.dataset = dataset
            return

        new_image_dataset = apply_shift(dataset, shift, dimension)

        self.outputs.dataset = Dataset(
            dataset=new_image_dataset,
            indices=dataset.indices,
            bg_indices=dataset.bg_indices,
            bg_dataset=dataset.bg_dataset,
        )
