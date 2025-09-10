from __future__ import annotations

import os

import numpy
from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from skimage.transform import rescale

from darfix.core.data import Data
from darfix.dtypes import Dataset
from darfix.dtypes import ImageDataset


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: Dataset
    """ Input dataset containing a stack of images """
    scale: float
    """Factor to rescale images of the dataset."""
    output_dir: str | MissingData = MISSING_DATA
    """ Output directory where the binned data will be saved. If not set, use the input dataset directory."""


class Binning(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    """Rescale images of a Darfix dataset by a given factor."""

    def run(self):
        input_dataset: Dataset = self.inputs.dataset
        dataset = input_dataset.dataset

        if len(dataset.data.shape) >= 4:
            # TODO: Is this expected ? Or should it be fixed for higher dimensionality ?
            raise ValueError("Binning cannot only be applied to 4D datasets or higher")

        scale = self.inputs.scale
        output_dir = self.get_input_value("output_dir", dataset.dir)
        os.makedirs(output_dir, exist_ok=True)

        # rescale data
        new_data = None
        for i, image in enumerate(dataset.data):
            simage = rescale(image, scale, anti_aliasing=True, preserve_range=True)
            if new_data is None:
                new_data = numpy.empty(
                    (len(dataset.data),) + simage.shape, dtype=dataset.data.dtype
                )
            new_data[i] = simage
            if self.cancelled:
                # if cancelled then self.outputs.dataset will be MISSING_DATA
                return

        data = new_data
        shape = data.shape
        data = data.view(Data)
        data.save(
            os.path.join(output_dir, "binned_data.hdf5"),
            new_shape=shape,
        )
        data.metadata = dataset.data.metadata
        shape = list(data.shape)[:-2]
        shape.append(data.shape[-2])
        shape.append(data.shape[-1])
        data = data.reshape(shape)

        new_dataset = ImageDataset(
            _dir=output_dir,
            data=data,
            dims=dataset.dims,
            transformation=dataset.transformation,
            in_memory=True,
            title=dataset.title,
        )

        self.outputs.dataset = Dataset(
            dataset=new_dataset,
            indices=input_dataset.indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )

    def cancel(self):
        """
        Cancel binning.
        """
        # Cancellation is very simple: binning is done image by image.
        # Between each image binning we check if the task has been cancelled.
        self.cancelled = True
