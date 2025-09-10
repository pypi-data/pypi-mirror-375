from __future__ import annotations

from ewokscore.missing_data import is_missing_data
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
from silx.gui import qt

from darfix import dtypes
from darfix.core.noiseremoval import NoiseRemovalOperation
from darfix.gui.noiseremoval.noiseRemovalWidget import NoiseRemovalDialog
from darfix.tasks.noiseremoval import NoiseRemoval


class NoiseRemovalWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=NoiseRemoval):
    name = "noise removal"
    description = "A widget to perform various noise removal operations"
    icon = "icons/noise_removal.png"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("operations",)

    def __init__(self):
        super().__init__()

        self._widget = NoiseRemovalDialog(self)
        self.mainArea.layout().addWidget(self._widget)
        self._widget.mainWindow.sigLaunchOperation.connect(
            self._execute_noise_removal_operation
        )
        self._current_operation: NoiseRemovalOperation | None = None
        self._widget.okSignal.connect(self.propagate_downstream)
        self._widget.abortSignal.connect(self.abort)

        self._first_init = True

    def _setCurrentOperation(self, operation: NoiseRemovalOperation | None):
        self._current_operation = operation
        self._widget.setIsComputing(bool(operation))

    def handleNewSignals(self) -> None:
        dataset = self.get_task_input_value("dataset")
        self.setDataset(dataset, pop_up=True)

        # Do not call super().handleNewSignals() to prevent propagation

    def showEvent(self, evt):
        super().showEvent(evt)

        if not self._first_init:
            return

        history = [
            NoiseRemovalOperation(ope)
            for ope in self.get_default_input_value("operations", [])
        ]
        self._first_init = False
        self._widget.mainWindow.setDefaultParameters(history)

        if len(history) > 0 and not is_missing_data(
            self.get_task_input_value("dataset")
        ):
            messagebox = qt.QMessageBox(
                qt.QMessageBox.Icon.Question,
                "Replay Operations ?",
                "Do you want to apply the following operations from last save now ?\n IF NOT, the history of operations will be cleared.\n\n"
                + "\n\n".join([f"{i} - {str(ope)}" for i, ope in enumerate(history)]),
                buttons=qt.QMessageBox.StandardButton.Yes
                | qt.QMessageBox.StandardButton.No,
            )
            ret = messagebox.exec()
            if ret == qt.QMessageBox.StandardButton.Yes:
                self.execute_ewoks_task_without_propagation()
                self._widget.mainWindow.setOperationHistory(history)

    def setDataset(self, dataset: dtypes.Dataset | None, pop_up=True):
        if dataset is None:
            return
        self._widget.setDataset(dataset)
        if pop_up:
            self.open()

    def _execute_noise_removal_operation(
        self, operation: NoiseRemovalOperation
    ) -> None:
        # Apply operations one after the other: take the previous output as input
        # Note:: the history is being kept by '_widget'
        output_dataset = self._widget.getOutputDataset()

        self.set_dynamic_input("dataset", output_dataset)
        self.set_dynamic_input("operations", [operation])

        self._setCurrentOperation(operation)
        self.execute_ewoks_task_without_propagation()

    def task_output_changed(self):
        self._setCurrentOperation(None)
        new_dataset: dtypes.Dataset | None = self.get_task_output_value("dataset", None)
        if new_dataset is None:
            return
        self._widget.setOutputDataset(new_dataset)

    def closeEvent(self, evt):
        super().closeEvent(evt)
        self._saveOperationHistory()

    def propagate_downstream(self, succeeded: bool | None = None):
        self._saveOperationHistory()
        super().propagate_downstream(succeeded)
        self.close()

    def _saveOperationHistory(self):
        self.set_default_input("operations", self._widget.getOperationHistory())

    def abort(self):
        self._widget.mainWindow.abortOperation(self._current_operation)
        self._setCurrentOperation(None)
