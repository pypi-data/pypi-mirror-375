from __future__ import annotations

from typing import Any

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from pydantic import Field

from darfix.dtypes import Dataset

from ..core.noiseremoval import NoiseRemovalOperation
from ..core.noiseremoval import apply_noise_removal_operation


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: Dataset
    """ Input dataset containing a stack of images """
    operations: list[dict[str, Any]] | MissingData = Field(
        default=MISSING_DATA,
        examples=[
            [
                {"type": "THRESHOLD", "parameters": {"bottom": 10.0, "top": 1000.0}},
                {"type": "HP", "parameters": {"kernel_size": 3}},
            ]
        ],
        description="""List of noise removal operations to apply to the dataset. Empty list if not provided."

        Available operations :

        - 'Operation.THRESHOLD': Threshold operation. Parameters: 'bottom' (float) and 'top' (float). Keep value only if it is between bottom and top.
        - 'Operation.HP': Hot Pixel removal using median filter operation. Parameters: 'kernel_size' (int).
        - 'Operation.BS': Background subtraction operation. Parameters: 'method' ("mean" | "median") and 'background_type' ("Data" | "Unused data (after partition)" | "Dark data").
        - 'Operation.MASK': Mask removal operation. Parameters: 'mask' (numpy.ndarray 2D containing 0 and 1 where 0 indicates the pixels to be removed).
        """,
    )


class NoiseRemoval(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    """Apply a list of noise removal operations on a Darfix dataset."""

    def run(self):
        input_dataset: Dataset = self.get_input_value("dataset")
        operations: list[NoiseRemovalOperation] = [
            NoiseRemovalOperation(operation)
            for operation in self.get_input_value("operations", [])
        ]

        dataset = input_dataset
        for operation in operations:
            new_darfix_dataset = apply_noise_removal_operation(dataset, operation)
            if new_darfix_dataset is None:
                continue

            dataset = Dataset(
                dataset=new_darfix_dataset,
                indices=input_dataset.indices,
                bg_dataset=input_dataset.bg_dataset,
                bg_indices=input_dataset.bg_indices,
            )

        self.outputs.dataset = dataset
