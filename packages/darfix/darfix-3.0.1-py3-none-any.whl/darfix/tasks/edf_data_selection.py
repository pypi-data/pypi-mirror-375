from __future__ import annotations

from ewokscore import Task
from ewokscore.missing_data import MISSING_DATA
from ewokscore.missing_data import MissingData
from ewokscore.model import BaseInputModel
from pydantic import ConfigDict
from pydantic import Field

from darfix import dtypes
from darfix.core.data_selection import load_process_data


class Inputs(BaseInputModel):
    model_config = ConfigDict(use_attribute_docstrings=True)
    filenames: list[str] | MissingData = Field(
        default=MISSING_DATA,
        examples=[["scan1.edf", "scan2.edf", "scan3.edf"]],
        description="List of EDF scan filenames to load. raw_filename or filenames should be provided.",
    )
    raw_filename: str | MissingData = MISSING_DATA
    """Filename of the raw data to load. Either this or filenames should be provided."""
    root_dir: str | MissingData = MISSING_DATA
    """Processed output directory. If not provided, will try to find PROCESSED_DATA directory."""
    in_memory: bool | MissingData = MISSING_DATA
    """If True, load the dataset in memory rather than keeping data on disk. Defaults to True."""
    dark_filename: str | MissingData = MISSING_DATA
    """Filename of the first dark image to use for background subtraction."""
    copy_files: bool | MissingData = MISSING_DATA
    title: str | MissingData = MISSING_DATA
    """Title of the dataset for display purpose. Empty if not provided."""


class EDFDataSelection(
    Task,
    input_model=Inputs,
    output_names=["dataset"],
):
    """Loads data from a set of EDF files in a darfix Dataset."""

    def run(self):
        in_memory = self.get_input_value("in_memory", True)
        copy_files = self.get_input_value("copy_files", True)
        dark_filename = self.get_input_value("dark_filename", None)
        root_dir = self.get_input_value("root_dir", None)
        title = self.get_input_value("title", "")

        filenames = self.get_input_value("filenames", None)
        if filenames is None:
            filenames = self.get_input_value("raw_filename", None)
            if filenames is None:
                raise ValueError(
                    "Either 'filenames' or 'raw_filename' should be provided"
                )

        dataset, indices, bg_indices, bg_dataset = load_process_data(
            filenames=filenames,
            root_dir=root_dir,
            dark_filename=dark_filename,
            in_memory=in_memory,
            copy_files=copy_files,
            title=title,
            isH5=False,
        )
        self.outputs.dataset = dtypes.Dataset(
            dataset=dataset,
            indices=indices,
            bg_indices=bg_indices,
            bg_dataset=bg_dataset,
        )
