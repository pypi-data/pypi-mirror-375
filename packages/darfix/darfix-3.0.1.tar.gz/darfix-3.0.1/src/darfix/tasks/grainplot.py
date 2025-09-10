from __future__ import annotations

import logging
import os
from typing import Literal

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from silx.io.dictdump import dicttonx

from darfix import dtypes

from ..core.dataset import ImageDataset
from ..core.grainplot import OrientationDistImage
from ..core.grainplot import compute_mosaicity
from ..core.grainplot import compute_orientation_dist_data
from ..core.grainplot import generate_grain_maps_nxdict
from ..core.grainplot import get_image_parameters

_logger = logging.getLogger(__file__)


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    dataset: dtypes.Dataset
    """ Input dataset containing a stack of images """
    dimensions: tuple[int, int] | MissingData = MISSING_DATA
    """Dimension indices to use for the maps. Default is (0, 1), which means the two first dimensions."""
    third_motor: int | MissingData = MISSING_DATA
    """Third motor index to use for the orientation distribution. Default is 0."""
    save_maps: bool | MissingData = MISSING_DATA
    """Whether to save the maps to file. Default is True."""
    filename: str | MissingData = MISSING_DATA
    """Only used if save_maps is True. Filename to save the maps to. Default is 'maps.h5' in the dataset directory."""
    orientation_img_origin: Literal["dims", "center"] | None | MissingData = (
        MISSING_DATA
    )
    "Origin for the orientation distribution image. Can be 'dims', 'center' or None. Default is 'dims'."


class GrainPlot(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    """Generates and saves maps of Center of Mass, FWHM, Skewness, Kurtosis, Orientation distribution and Mosaicity."""

    def run(self):
        input_dataset: dtypes.Dataset = self.inputs.dataset
        default_filename = os.path.join(input_dataset.dataset._dir, "maps.h5")
        filename: str = self.get_input_value("filename", default_filename)
        dimensions: tuple[int, int] = self.get_input_value("dimensions", (0, 1))
        save_maps: bool = self.get_input_value("save_maps", True)
        third_motor: int | None = self.get_input_value("third_motor", None)
        orientation_img_origin: str | None = self.get_input_value(
            "orientation_img_origin", "dims"
        )

        dataset: ImageDataset = input_dataset.dataset
        moments = dataset.apply_moments()

        # mosaicity and orientation can only be computed for 2D+ datasets
        if dataset.dims.ndim > 1:
            dimension1, dimension2 = dimensions

            mosaicity = compute_mosaicity(
                moments,
                x_dimension=dimension1,
                y_dimension=dimension2,
            )

            orientation_dist_data = compute_orientation_dist_data(
                dataset,
                x_dimension=dimension1,
                y_dimension=dimension2,
                third_motor=third_motor,
            )
            assert orientation_dist_data is not None

            if (
                orientation_img_origin is not None
                and orientation_img_origin != "dims"
                and orientation_img_origin != "center"
            ):
                _logger.warning(
                    f'Unexpected value for orientation_img_origin. Expected dims, center or None, got {orientation_img_origin}. Will use "dims" instead.'
                )
                orientation_img_origin = "dims"

            image_parameters = get_image_parameters(
                dataset,
                x_dimension=dimension1,
                y_dimension=dimension2,
                origin=orientation_img_origin,
            )
            orientation_dist_image = OrientationDistImage(
                xlabel=image_parameters.xlabel,
                ylabel=image_parameters.ylabel,
                scale=image_parameters.scale,
                origin=image_parameters.origin,
                data=orientation_dist_data.data,
                as_rgb=orientation_dist_data.as_rgb,
                contours=dict(),
            )
        else:
            mosaicity = None
            orientation_dist_image = None

        # Save data if asked
        if save_maps:
            nxdict = generate_grain_maps_nxdict(
                dataset, mosaicity, orientation_dist_image
            )
            dicttonx(nxdict, filename)

        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=input_dataset.indices,
            bg_indices=input_dataset.bg_indices,
            bg_dataset=input_dataset.bg_dataset,
        )
