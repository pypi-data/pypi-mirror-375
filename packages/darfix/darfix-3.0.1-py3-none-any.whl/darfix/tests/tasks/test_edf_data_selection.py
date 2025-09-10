from __future__ import annotations

import pytest

from darfix import dtypes
from darfix.tasks.edf_data_selection import EDFDataSelection
from orangecontrib.darfix import tutorials

try:
    from importlib.resources import files as resource_files
except ImportError:
    from importlib_resources import files as resource_files


@pytest.mark.parametrize("title", (None, "test_title"))
@pytest.mark.parametrize("in_memory", (True, False))
@pytest.mark.parametrize("copy_files", (True, False))
@pytest.mark.parametrize("with_bg", (True, False))
def test_edf_data_selection(
    tmp_path, in_memory: bool, copy_files: bool, with_bg: bool, title: None | str
):

    image0 = resource_files(tutorials).joinpath("edf_dataset", "strain_0000.edf")
    image1 = resource_files(tutorials).joinpath("edf_dataset", "strain_0001.edf")

    task = EDFDataSelection(
        inputs={
            "filenames": (image0, image1),
            "root_dir": str(tmp_path / "test_edf_selection"),
            "in_memory": in_memory,
            "copy_files": copy_files,
            "dark_filename": str(image0) if with_bg else None,
            "title": title,
        }
    )
    task.run()
    assert isinstance(task.outputs.dataset, dtypes.Dataset)
    if with_bg:
        assert task.outputs.dataset.bg_dataset is not None
    else:
        assert task.outputs.dataset.bg_dataset is None
    assert task.outputs.dataset.dataset.title == (title if title else "")
