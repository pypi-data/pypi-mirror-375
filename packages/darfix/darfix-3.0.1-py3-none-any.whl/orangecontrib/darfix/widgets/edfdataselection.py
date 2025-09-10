import logging
from functools import partial

from ewokscore.missing_data import MISSING_DATA
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from silx.gui import qt

from darfix.gui.data_selection.edf import EDFDatasetSelectionWidget
from darfix.tasks.edf_data_selection import EDFDataSelection

_logger = logging.getLogger(__file__)


class EDFDataSelectionWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=EDFDataSelection):
    """
    Widget to select the data to be used in the dataset.
    """

    name = "EDF data selection"
    icon = "icons/upload_edf.svg"
    want_main_area = True
    want_control_area = False

    priority = 2

    def __init__(self):
        super().__init__()

        self._widget = EDFDatasetSelectionWidget()
        types = qt.QDialogButtonBox.Ok
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)

        self.mainArea.layout().addWidget(self._widget)
        self.mainArea.layout().addWidget(_buttons)

        _buttons.accepted.connect(self.execute_ewoks_task)

        # load settings
        filenames = self.get_default_input_value("filenames", MISSING_DATA)
        if filenames is not MISSING_DATA:
            self._widget.setRawFilenames(files=filenames)
        raw_filename = self.get_default_input_value("raw_filename", MISSING_DATA)
        if raw_filename is not MISSING_DATA:
            self._widget.setRawFilename(raw_filename)
        in_memory = self.get_default_input_value("in_memory", True)
        self._widget.setKeepDataOnDisk(not in_memory)
        dark_filename = self.get_default_input_value("dark_filename", MISSING_DATA)
        if dark_filename is not MISSING_DATA:
            self._widget.setDarkFilename(dark_filename)
        treated_data_dir = self.get_task_input_value("root_dir", "")
        self._widget.setTreatedDir(treated_data_dir)

        # connect signal / slot
        self._widget.sigDarkDataInfosChanged.connect(self._darkInfosChanged)
        self._widget.sigRawDataInfosChanged.connect(self._rawInfosChanged)
        self._widget.sigTreatedDirInfoChanged.connect(self._treatedDataDirChanged)
        # connect signal / slot
        self.task_executor.finished.connect(
            self.information,
        )
        self.task_executor.started.connect(
            partial(self.information, "Downloading dataset")
        )

        # make sure ewoks input are up to date
        self._rawInfosChanged()
        self._darkInfosChanged()
        self._treatedDataDirChanged()

    def _rawInfosChanged(self):
        self.set_default_input(
            "filenames",
            self._widget.getRawFilenames() or None,
        )
        self.set_default_input(
            "raw_filename",
            self._widget.getRawFilename() or None,
        )
        self.set_default_input(
            "in_memory",
            not self._widget.keepDataOnDisk(),
        )
        self.set_default_input("title", self._widget.getWorkflowTitle() or None)

    def _darkInfosChanged(self):
        self.set_default_input("dark_filename", self._widget.getDarkFilename() or None)

    def _treatedDataDirChanged(self):
        self.set_default_input("root_dir", self._widget.getTreatedDir() or None)
