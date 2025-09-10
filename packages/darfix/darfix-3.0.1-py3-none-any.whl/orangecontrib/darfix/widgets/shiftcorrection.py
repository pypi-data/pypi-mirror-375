from __future__ import annotations

import numpy
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from silx.gui import qt

from darfix import dtypes
from darfix.gui.shiftcorrection.shiftCorrectionWidget import ShiftCorrectionDialog
from darfix.tasks.shiftcorrection import ShiftCorrection


class ShiftCorrectionWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=ShiftCorrection):
    """
    Widget to make the shift correction of a dataset.
    """

    name = "shift correction"
    description = "A widget to perform shift correction"
    icon = "icons/shift_correction.svg"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("shift", "dimension")

    def __init__(self):
        super().__init__()
        qt.QLocale.setDefault(qt.QLocale("en_US"))

        self._widget = ShiftCorrectionDialog(parent=self)
        self._loadCorrectionInputs()
        self.mainArea.layout().addWidget(self._widget)
        self._widget.correctSignal.connect(self.execute_shift_correction)
        self._widget.okSignal.connect(self.propagate_downstream)

    def handleNewSignals(self) -> None:
        dataset = self.get_task_input_value("dataset", None)
        if dataset is not None:
            self.setDataset(dataset, pop_up=True)

        # Do not call super().handleNewSignals() to prevent propagation

    def setDataset(self, dataset: dtypes.Dataset, pop_up=True):
        self.set_dynamic_input("dataset", dataset)
        self._widget.setDataset(dataset)
        if pop_up:
            self.open()

    def execute_shift_correction(self):
        self._widget.onComputingStart()
        self._saveCorrectionInputs()
        self.execute_ewoks_task_without_propagation()

    def task_output_changed(self) -> None:
        self._widget.onComputingFinish()
        new_dataset: dtypes.Dataset | None = self.get_task_output_value("dataset", None)
        if new_dataset is None:
            return
        self._widget.setOutputDataset(new_dataset.dataset)

    def closeEvent(self, evt):
        self._saveCorrectionInputs()
        super().closeEvent(evt)

    def _saveCorrectionInputs(self):
        inputs = self._widget.getCorrectionInputs()
        for key, value in inputs.items():
            if isinstance(value, numpy.ndarray):
                value = value.tolist()
            self.set_default_input(key, value)

    def _loadCorrectionInputs(self):
        self._widget.setCorrectionInputs(
            self.get_task_input_value("dimension", None),
            self.get_task_input_value("shift", (0, 0)),
        )

    def propagate_downstream(self, succeeded: bool | None = None):
        super().propagate_downstream(succeeded)
        self.close()
