import os

import fabio
import numpy
import pytest
from ewoksorange.tests.conftest import qtapp  # noqa F401

from darfix import dtypes
from darfix.gui.utils.qsignalspy import QSignalSpy
from darfix.tests.utils import createRandomEDFDataset
from orangecontrib.darfix.widgets.edfdataselection import EDFDataSelectionWidgetOW


@pytest.mark.parametrize("workflow_title", (None, "my_workflow"))
@pytest.mark.parametrize("in_memory", (True, False))
@pytest.mark.parametrize("with_dark", (True, False))
@pytest.mark.parametrize("processed_data_dir", (None, "PROCESSED_DATA"))
@pytest.mark.parametrize("provide_single_raw_file", (True, False))
@pytest.mark.skipif(QSignalSpy is None, reason="Unable to import QSignalSpy")
def test_EDFDataSelectionWidgetOW(
    provide_single_raw_file,
    in_memory,
    workflow_title,
    processed_data_dir,
    with_dark,
    tmp_path,
    qtapp,  # noqa F811
):
    """
    test the HDF5ataSelectionWidgetOW
    """
    test_data_dir = tmp_path / "test_EDFDataSelectionWidgetOW"
    test_data_dir.mkdir()
    raw_data_dir = test_data_dir / "rawData"
    raw_data_dir.mkdir()

    dims = (100, 100)
    createRandomEDFDataset(
        dims=dims, nb_data_files=10, header=True, _dir=str(raw_data_dir)
    )

    window = EDFDataSelectionWidgetOW()
    assert window.get_task_input_values() == {
        "in_memory": True,
    }

    # make sure if no input provided then this will raise an error.
    waiter = QSignalSpy(window.task_executor.finished)
    window.execute_ewoks_task()
    # wait for the task_executor to be finished
    waiter.wait(5000)
    assert window.task_succeeded is False

    # test once the widget is set
    expected_result = {}
    filesnames = [
        os.path.join(str(raw_data_dir), file) for file in os.listdir(raw_data_dir)
    ]
    filesnames = sorted(filesnames)
    if provide_single_raw_file:
        window._widget.setRawFilename(filesnames[0])
        expected_result["raw_filename"] = filesnames[0]
    else:
        window._widget.setRawFilenames(filesnames)
        expected_result["filenames"] = filesnames
    window._widget.setKeepDataOnDisk(not in_memory)
    expected_result["in_memory"] = in_memory

    if workflow_title:
        window._widget.setWorkflowTitle(workflow_title)
        expected_result["title"] = workflow_title

    if processed_data_dir:
        window._widget.setTreatedDir(processed_data_dir)
        expected_result["root_dir"] = processed_data_dir

    if with_dark:
        dark_data_dir = test_data_dir / "dark"
        dark_data_dir.mkdir()
        dark_file = os.path.join(str(dark_data_dir), "my_dark.edf")
        image = fabio.edfimage.EdfImage(data=numpy.random.random(dims))
        image.write(dark_file)
        window._widget.setDarkFilename(dark_file)
        expected_result["dark_filename"] = dark_file

    assert window.get_task_input_values() == expected_result
    window.execute_ewoks_task()
    # wait for the task_executor to be finished
    waiter.wait(5000)
    assert window.task_succeeded is True
    dataset = window.get_task_output_value("dataset")
    assert isinstance(dataset, dtypes.Dataset), f"type is {type(dataset)}"
    data = dataset.dataset.data
    bg_dataset = dataset.bg_dataset
    assert data is not None
    if with_dark:
        assert bg_dataset is not None
    else:
        assert bg_dataset is None

    if processed_data_dir:
        processing_dir = dataset.dataset.dir
        assert processing_dir == os.path.join(processed_data_dir, "treated")

    title = dataset.dataset.title
    if workflow_title is None:
        assert title == ""
    else:
        assert title == workflow_title
