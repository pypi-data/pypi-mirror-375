from __future__ import annotations

import os.path
from typing import Literal

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from silx.io.dictdump import dicttonx

from ..core.rocking_curves import compute_residuals
from ..core.rocking_curves import generate_rocking_curves_nxdict
from ..dtypes import Dataset


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: Dataset
    """ Input dataset containing a stack of images """
    int_thresh: float | MissingData = MISSING_DATA
    """If provided, only the rocking curves with higher ptp (peak to peak) value > int_thresh are fitted, others are assumed to be noise and will be discarded"""
    method: Literal["trf", "lm", "dogbox"] = MISSING_DATA
    "Method to use for the rocking curves fit. 'trf' is the default method.",
    output_filename: str | MissingData | None = MISSING_DATA
    """Output filename to save the rocking curves results. Result is not saved if not provided"""


class RockingCurves(
    Task,
    input_model=Inputs,
    output_names=["dataset", "maps"],
):
    """Analyze the rocking curve of each pixel of each image of the darfix dataset by fitting to a peak shape, e.g. a Gaussian.

    Related article : https://pmc.ncbi.nlm.nih.gov/articles/PMC10161887/#sec3.3.1
    """

    def run(self):
        input_dataset: Dataset = self.inputs.dataset
        int_thresh: float | None = (
            float(self.inputs.int_thresh) if self.inputs.int_thresh else None
        )
        method: str | None = self.get_input_value("method", None)
        default_filename = os.path.join(input_dataset.dataset._dir, "rocking_curves.h5")
        output_filename: str | None = self.get_input_value(
            "output_filename", default_filename
        )

        if output_filename and os.path.isfile(output_filename):
            raise OSError(
                f"""Cannot launch rocking curves fit: saving destination {output_filename} already exists.
                Change the `output_filename` input or set it to None to disable saving."""
            )

        dataset = input_dataset.dataset
        indices = input_dataset.indices
        new_image_dataset, maps = dataset.apply_fit(
            indices=indices, int_thresh=int_thresh, method=method
        )

        if output_filename is not None:
            nxdict = generate_rocking_curves_nxdict(
                new_image_dataset,
                maps,
                residuals=compute_residuals(new_image_dataset, dataset, indices),
            )
            dicttonx(nxdict, output_filename)

        self.outputs.dataset = Dataset(
            dataset=new_image_dataset,
            indices=indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )
        self.outputs.maps = maps
