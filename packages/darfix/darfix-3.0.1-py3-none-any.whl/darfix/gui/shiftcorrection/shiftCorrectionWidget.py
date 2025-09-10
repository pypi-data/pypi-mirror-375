from __future__ import annotations

import logging
from typing import Any
from typing import Dict

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow

import darfix

from ... import dtypes
from ...core.data import Operation
from ...core.dataset import ImageDataset
from ..chooseDimensions import ChooseDimensionDock
from ..operationThread import OperationThread
from ..utils.message import missing_dataset_msg
from ..utils.standardButtonBox import StandardButtonBox
from ..utils.vspacer import VSpacer
from .shiftInput import ShiftInput

_logger = logging.getLogger(__file__)


class ShiftCorrectionDialog(qt.QDialog):
    """
    A widget to apply shift correction to a stack of images
    """

    okSignal = qt.Signal()
    correctSignal = qt.Signal()
    outputChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(qt.Qt.WindowType.Widget)

        self._mainWindow = _ShiftCorrectionWidget(parent=self)
        self._mainWindow.setAttribute(qt.Qt.WidgetAttribute.WA_DeleteOnClose)
        layout = qt.QVBoxLayout()
        layout.addWidget(self._mainWindow)

        self._buttons = StandardButtonBox(parent=self)
        self._toggleOkButton()
        layout.addWidget(self._buttons)

        self.setLayout(layout)

        self._buttons.accepted.connect(self.okSignal.emit)
        self._buttons.rejected.connect(self.abort)
        self._buttons.resetButton.clicked.connect(self.resetOutputDataset)
        self._mainWindow.computingStarted.connect(self.onComputingStart)
        self._mainWindow.computingFinished.connect(self.onComputingFinish)
        self._mainWindow._shiftWidget.correctionB.clicked.connect(
            self.correctSignal.emit
        )
        self.outputChanged.connect(self._toggleOkButton)

    def _toggleOkButton(self):
        has_output_dataset = self._mainWindow._corrected_dataset is not None
        self._buttons.okButton.setEnabled(has_output_dataset)

    def setDataset(self, dataset: dtypes.Dataset) -> None:
        if dataset.dataset is not None:
            self._buttons.setEnabled(True)
            self._mainWindow.setDataset(dataset)

    def setOutputDataset(self, dataset: ImageDataset) -> None:
        self._mainWindow.setOutputDataset(dataset)
        self.outputChanged.emit()

    def resetOutputDataset(self) -> None:
        self._mainWindow.resetStack()
        self.outputChanged.emit()

    def onComputingStart(self):
        self._setIsComputing(True)

    def onComputingFinish(self):
        self._setIsComputing(False)
        # Output may have changed after computation
        self.outputChanged.emit()

    def _setIsComputing(self, isComputing: bool):
        self._buttons.setIsComputing(isComputing)
        self._mainWindow._shiftWidget.findShiftB.setDisabled(isComputing)
        self._mainWindow._shiftWidget.correctionB.setDisabled(isComputing)

    def getStackViewColormap(self) -> Colormap:
        return self._mainWindow._sv.getColormap()

    def setStackViewColormap(self, colormap: Colormap):
        self._mainWindow._sv.setColormap(colormap)

    def getCorrectionInputs(self) -> Dict[str, Any]:
        return self._mainWindow.getCorrectionInputs()

    def setCorrectionInputs(
        self,
        dimension: int | None,
        shift: tuple[Any, Any] | tuple[tuple[Any, Any], ...],
    ):
        self._mainWindow.setCorrectionInputs(dimension, shift)

    def abort(self):
        self._setIsComputing(False)
        self._mainWindow.abort()


class _ShiftCorrectionWidget(qt.QMainWindow):
    """
    A widget to apply shift correction to a stack of images
    """

    computingStarted = qt.Signal()
    computingFinished = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowFlags(qt.Qt.WindowType.Widget)

        self._filtered_shift = None
        self._dimension = None
        self._corrected_dataset = None
        self._input_dataset = None
        self.indices = None
        self.bg_indices = None
        self.bg_dataset = None

        self._shiftWidget = ShiftInput(parent=self)
        self._shiftWidget.correctionB.setEnabled(False)

        self._sv = StackViewMainWindow()
        self._sv.setColormap(
            Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME, normalization="linear")
        )
        self._sv.setKeepDataAspectRatio(True)
        self.setCentralWidget(self._sv)
        self._chooseDimensionDock = ChooseDimensionDock(self)
        self._chooseDimensionDock.widget.layout().addWidget(VSpacer())

        self._chooseDimensionDock.hide()
        self.addDockWidget(
            qt.Qt.DockWidgetArea.RightDockWidgetArea, self._chooseDimensionDock
        )
        self.addDockWidget(qt.Qt.DockWidgetArea.RightDockWidgetArea, self._shiftWidget)

        self._shiftWidget.findShiftB.clicked.connect(self._launchFindShift)
        self._shiftWidget.shiftChanged.connect(self._updateFilteredShift)
        self._chooseDimensionDock.widget.filterChanged.connect(self._filterStack)
        self._chooseDimensionDock.widget.stateDisabled.connect(self._wholeStack)

    def getShift(self) -> numpy.ndarray:
        return numpy.array(self._shiftWidget.getShift())

    def setShift(self, shift: numpy.ndarray):
        self._shiftWidget.setShift((shift[0], shift[1]))

    def setDataset(self, dataset: dtypes.Dataset):
        """Saves the dataset and updates the stack with the dataset data."""
        self._input_dataset = dataset.dataset
        self._corrected_dataset = None
        self._shiftWidget.correctionB.setEnabled(True)
        self._sv.setKeepDataAspectRatio(True)
        self._sv.setGraphTitle(self._input_dataset.title)
        if len(self._input_dataset.data.shape) > 3:
            self._chooseDimensionDock.show()
            self._chooseDimensionDock.widget.setDimensions(self._input_dataset.dims)
        if not self._chooseDimensionDock.widget._checkbox.isChecked():
            self._wholeStack()

    def abort(self):
        if self._input_dataset:
            self._input_dataset.stop_operation(Operation.SHIFT)

    def resetStack(self):
        self._corrected_dataset = None
        self._setStack(self._input_dataset)
        self._filtered_shift = None

    def _updateFilteredShift(self):
        if self._filtered_shift is None:
            return
        self._filtered_shift[self._dimension[1]] = self._shiftWidget.getShift()

    def _launchFindShift(self):
        dataset = self._input_dataset
        if dataset is None:
            missing_dataset_msg()
            return

        if self._filtered_shift is not None:
            thread = self._findShiftAlongDimThread(dataset)
        else:
            thread = self._findShiftThread(dataset)

        self.thread_detection = thread
        self.thread_detection.start()
        self.computingStarted.emit()

    def _findShiftThread(self, dataset: ImageDataset):
        thread = OperationThread(self, dataset.find_shift)
        thread.setArgs(self._dimension, indices=self.indices)
        thread.finished.connect(self._updateShift)

        return thread

    def _findShiftAlongDimThread(self, dataset: ImageDataset):
        thread = OperationThread(self, dataset.find_shift_along_dimension)
        thread.setArgs(self._dimension[0], indices=self.indices)
        thread.finished.connect(self._updateShiftAlongDim)

        return thread

    def _updateShift(self):
        self.thread_detection.finished.disconnect(self._updateShift)
        self.computingFinished.emit()
        self.setShift(numpy.round(self.thread_detection.data[:, 1], 5))

    def _updateShiftAlongDim(self):
        self.thread_detection.finished.disconnect(self._updateShiftAlongDim)
        self.computingFinished.emit()
        shifts = []
        for shift in self.thread_detection.data:
            try:
                shifts.append(numpy.round(shift[:, 1], 5))
            except (IndexError, TypeError):
                shifts.append([0, 0])
        self._filtered_shift = numpy.array(shifts)
        self.setShift(self._filtered_shift[self._dimension[1][0]])

    def getCorrectionInputs(self) -> Dict[str, Any]:
        if not self._shiftWidget.filterCB.isChecked():
            return {"shift": self.getShift(), "dimension": None}

        return {"shift": self._filtered_shift, "dimension": self._dimension[0][0]}

    def setCorrectionInputs(
        self,
        dimension_idx: int | None,
        shift: tuple[Any, Any] | tuple[tuple[Any, Any], ...],
    ):
        """
        Set widget parameters from .ows save

        :param dimension_idx: dimension_idx is the index of the chosen dimension
        :param shift : shift is (shift_x, shift_y) when dimension_idx is None, else this is (shift_x1, shift_y1), ..., (shift_xn, shift_yn) with n = the dimension size
        """
        if dimension_idx is not None:
            # Temporary code to warn user (only once) that this feature is not yet implemented.
            _logger.warning(
                "Load saved correction inputs when filtered by dimension is not implemented for now."
            )
            self.setShift((0, 0))
        else:
            self.setShift(shift)

    def setOutputDataset(self, dataset: ImageDataset):
        self._corrected_dataset = dataset
        self._setStack(self._corrected_dataset)

    def _setStack(self, dataset: ImageDataset | None):
        if dataset is None:
            return

        nframe = self._sv.getFrameNumber()
        self._sv.setStack(dataset.get_data(self.indices, self._dimension))
        self._sv.setFrameNumber(nframe)

    def _clearStack(self):
        self._sv.setStack(None)
        self._shiftWidget.correctionB.setEnabled(False)

    def _filterStack(self, dimension_indices: list[int], value_indices: list[int]):
        self._dimension = [dimension_indices, value_indices]

        if self._input_dataset.dims.ndim == 2:
            stack_size = self._input_dataset.dims.get(dimension_indices[0]).size
            reset_shift = (
                self._filtered_shift is None
                or self._filtered_shift.shape[0] != stack_size
            )

            self._shiftWidget.filterCB.show()
            if reset_shift:
                self._filtered_shift = numpy.zeros((stack_size, 2))
            self.setShift(self._filtered_shift[value_indices[0]])

        if self._corrected_dataset:
            self._setStack(self._corrected_dataset)
        else:
            self._setStack(self._input_dataset)

    def _wholeStack(self):
        self._dimension = None
        self._filtered_shift = None
        self._shiftWidget.filterCB.hide()
        if self._corrected_dataset:
            self._setStack(self._corrected_dataset)
        else:
            self._setStack(self._input_dataset)
