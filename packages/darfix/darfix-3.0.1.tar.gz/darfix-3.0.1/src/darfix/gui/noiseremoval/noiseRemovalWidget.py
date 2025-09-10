from __future__ import annotations

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow

from darfix import config
from darfix import dtypes
from darfix.core.data import Operation
from darfix.core.dataset import ImageDataset
from darfix.core.imageOperations import Method
from darfix.core.noiseremoval import BackgroundType
from darfix.core.noiseremoval import NoiseRemovalOperation

from ..utils.standardButtonBox import StandardButtonBox
from .operationHistory import OperationHistoryWidget
from .parametersWidget import ParametersWidget


class NoiseRemovalDialog(qt.QDialog):
    """
    Dialog with `NoiseRemovalWidget` as main window and standard buttons.
    """

    okSignal = qt.Signal()
    abortSignal = qt.Signal()

    def __init__(self, parent=None):
        qt.QDialog.__init__(self, parent)
        self.setWindowFlags(qt.Qt.WindowType.Widget)
        self._buttons = StandardButtonBox(self)
        self._buttons.setEnabled(False)
        self.mainWindow = _NoiseRemovalWidget(parent=self)
        self.mainWindow.setAttribute(qt.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.mainWindow)
        self.layout().addWidget(self._buttons)

        self._buttons.accepted.connect(self.okSignal.emit)
        self._buttons.resetButton.clicked.connect(self.mainWindow.resetStack)
        self._buttons.rejected.connect(self.abortSignal.emit)

        self.mainWindow._operationHistory.sigHistoryChanged.connect(self._toggleOk)

    def _toggleOk(self, operations: list[NoiseRemovalOperation]):
        ok_button = self._buttons.button(qt.QDialogButtonBox.Ok)
        assert ok_button is not None
        ok_button.setEnabled(len(operations) > 0)

    def setDataset(self, dataset: dtypes.Dataset):
        self._buttons.setEnabled(True)
        self.mainWindow.setDataset(dataset)

    def getOutputDataset(self) -> dtypes.Dataset:
        return self.mainWindow.getDataset()

    def setOutputDataset(self, dataset: dtypes.Dataset):
        output_dataset = dataset.dataset
        self.mainWindow._output_dataset = output_dataset
        self.mainWindow.setStack(output_dataset)

    def getOperationHistory(self):
        return self.mainWindow._operationHistory.getHistory()

    def setIsComputing(self, isComputing: bool):
        self.mainWindow.setIsComputing(isComputing)
        self._buttons.setIsComputing(isComputing)


class _NoiseRemovalWidget(qt.QWidget):
    """
    Widget to apply noise removal from a dataset.
    For now it can apply both background subtraction and hot pixel removal.
    For background subtraction the user can choose the background to use:
    dark frames, low intensity data or all the data. From these background
    frames, an image is computed either using the mean or the median.
    """

    sigLaunchOperation = qt.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._input_dataset: ImageDataset | None = None
        self._output_dataset: ImageDataset | None = None
        self.indices: numpy.ndarray | None = None
        self.bg_indices: numpy.ndarray | None = None
        self.bg_dataset: ImageDataset | None = None
        self.setWindowFlags(qt.Qt.WindowType.Widget)

        self._parametersWidget = ParametersWidget()
        self._sv = StackViewMainWindow()
        self._sv.setColormap(
            Colormap(
                name=config.DEFAULT_COLORMAP_NAME,
                normalization=config.DEFAULT_COLORMAP_NORM,
            )
        )
        self._sv.setKeepDataAspectRatio(True)
        self._size = None
        self._method = None
        self._background = self._parametersWidget.bsBackgroundCB.currentText()
        self._bottom_threshold = self._parametersWidget.bottomLE.text()
        self._top_threshold = self._parametersWidget.topLE.text()
        self._step = self._parametersWidget.step.text()
        self._chunks = [
            int(self._parametersWidget.verticalChunkSize.text()),
            int(self._parametersWidget.horizontalChunkSize.text()),
        ]

        self._operationHistory = OperationHistoryWidget()

        layout = qt.QVBoxLayout()
        layout.addWidget(self._sv)
        layout.addWidget(self._parametersWidget)
        layout.addWidget(self._operationHistory)
        self.setLayout(layout)

        # Add connections
        self._parametersWidget.computeBS.clicked.connect(
            self._launchBackgroundSubtraction
        )
        self._parametersWidget.computeHP.clicked.connect(self._launchHotPixelRemoval)
        self._parametersWidget.computeTP.clicked.connect(self._launchThresholdRemoval)
        self._parametersWidget.computeMR.clicked.connect(self._launchMaskRemoval)
        self._parametersWidget.bsMethodsCB.currentTextChanged.connect(
            self._toggleMethod
        )
        self._parametersWidget.bsBackgroundCB.currentIndexChanged.connect(
            self._toggleOnDiskWidget
        )

    def setDataset(self, dataset: dtypes.Dataset):
        """Saves the dataset and updates the stack with the dataset data."""

        self._operationHistory.clear()

        self._dataset = dataset.dataset
        self._output_dataset = dataset.dataset
        self.indices = dataset.indices
        if self._dataset.title != "":
            self._sv.setTitleCallback(lambda idx: self._dataset.title)
        self.setStack()
        self.bg_indices = dataset.bg_indices
        self.bg_dataset = dataset.bg_dataset

        self._parametersWidget.computeBS.show()
        self._parametersWidget.computeHP.show()
        self._parametersWidget.computeTP.show()
        self._parametersWidget.computeMR.show()

        """
        Sets the available background for the user to choose.
        """
        self._parametersWidget.bsBackgroundCB.clear()
        if dataset.bg_dataset is not None:
            self._parametersWidget.bsBackgroundCB.addItem(
                BackgroundType.DARK_DATA.value
            )
        if dataset.bg_indices is not None:
            self._parametersWidget.bsBackgroundCB.addItem(
                BackgroundType.UNUSED_DATA.value
            )
        self._parametersWidget.bsBackgroundCB.addItem(BackgroundType.DATA.value)

        # TODO: This fails when using a dataset with `in_memory=False`
        # self._parametersDock.topLE.setText(str(int(self._dataset.get_data().max()) + 1))

    def _launchBackgroundSubtraction(self):
        self._background = self._parametersWidget.bsBackgroundCB.currentText()

        if self._parametersWidget.onDiskWidget.isVisible():
            if self._parametersWidget.onDiskCheckbox.isChecked():
                self._step = None
                self._chunks = [
                    int(self._parametersWidget.verticalChunkSize.text()),
                    int(self._parametersWidget.horizontalChunkSize.text()),
                ]
            else:
                self._chunks = None
                self._step = int(self._parametersWidget.step.text())
        else:
            self._step = None
            self._chunks = None

        self._method = self._parametersWidget.bsMethodsCB.currentText()

        operation = NoiseRemovalOperation(
            type=Operation.BS,
            parameters={
                "method": self.method,
                "step": self._step,
                "chunks": self._chunks,
                "background_type": self._background,
            },
        )
        self._launchOperationInThread(operation)

    def _launchHotPixelRemoval(self):
        self._size = self._parametersWidget.hpSizeCB.currentText()

        operation = NoiseRemovalOperation(
            type=Operation.HP,
            parameters={
                "kernel_size": int(self._size),
            },
        )
        self._launchOperationInThread(operation)

    def _launchThresholdRemoval(self):
        self._bottom_threshold = self._parametersWidget.bottomLE.text()
        self._top_threshold = self._parametersWidget.topLE.text()

        operation = NoiseRemovalOperation(
            type=Operation.THRESHOLD,
            parameters={
                "bottom": int(self._bottom_threshold),
                "top": int(self._top_threshold),
            },
        )
        self._launchOperationInThread(operation)

    def _launchMaskRemoval(self):
        if self._output_dataset is None:
            return
        mask = self.mask
        if mask is None:
            return
        operation = NoiseRemovalOperation(
            type=Operation.MASK,
            parameters={"mask": mask},
        )
        self._launchOperationInThread(operation)

    def _launchOperationInThread(self, operation: NoiseRemovalOperation):
        self._operationHistory.append(operation)
        self.sigLaunchOperation.emit(operation)

    def abortOperation(self, operation: NoiseRemovalOperation | None):
        if operation is None or self._output_dataset is None:
            return
        self._output_dataset.stop_operation(operation["type"])
        self._operationHistory.pop()

    def setIsComputing(self, isComputing: bool):
        self._parametersWidget.computeBS.setDisabled(isComputing)
        self._parametersWidget.computeHP.setDisabled(isComputing)
        self._parametersWidget.computeTP.setDisabled(isComputing)
        self._parametersWidget.computeMR.setDisabled(isComputing)

    def _toggleMethod(self, text):
        if text == Method.mean.value:
            self._parametersWidget.onDiskWidget.hide()
        elif text == Method.median.value:
            self._toggleOnDiskWidget(
                self._parametersWidget.bsBackgroundCB.currentIndex()
            )

    def _toggleOnDiskWidget(self, index):
        if self._dataset is None:
            return
        if self._parametersWidget.bsMethodsCB.currentText() == Method.median.value:
            if self.bg_dataset is None:
                (
                    self._parametersWidget.onDiskWidget.hide()
                    if self._dataset.in_memory
                    else self._parametersWidget.onDiskWidget.show()
                )
            elif not (index or self.bg_dataset.in_memory) or (
                index and not self._dataset.in_memory
            ):
                self._parametersWidget.onDiskWidget.show()
            else:
                self._parametersWidget.onDiskWidget.hide()
        else:
            self._parametersWidget.onDiskWidget.hide()

    def getDataset(self) -> dtypes.Dataset:
        if self._output_dataset is None:
            raise ValueError("Load a dataset before trying to get a new one !")
        return dtypes.Dataset(
            dataset=self._output_dataset,
            indices=self.indices,
            bg_indices=self.bg_indices,
            bg_dataset=self.bg_dataset,
        )

    def resetStack(self):
        self._operationHistory.clear()
        self._output_dataset = self._dataset
        self.setStack()

    def clearStack(self):
        self._sv.setStack(None)

    def getStack(self):
        stack = self._sv.getStack(copy=False, returnNumpyArray=True)
        if stack is None:
            return None
        return stack[0]

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        new_dataset = dataset if dataset is not None else self._dataset
        if new_dataset is None:
            return
        old_nframe = self._sv.getFrameNumber()
        self._sv.setStack(new_dataset.get_data(self.indices))
        self._sv.setFrameNumber(old_nframe)

    def setDefaultParameters(self, operations: list[NoiseRemovalOperation]):
        """
        Set default values un widget parameters based on previous user history

        :param history: previous user history
        """
        self._parametersWidget.set_default_values(operations)

    def setOperationHistory(self, operations: list[NoiseRemovalOperation]):
        self._operationHistory.setHistory(operations)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        self._parametersWidget.hpSizeCB.setCurrentText(size)

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        self._method = method
        self._parametersWidget.bsMethodsCB.setCurrentText(method)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, step):
        self._step = step
        if step is not None:
            self._parametersWidget.step.setText(str(step))

    @property
    def chunks(self):
        return self._chunks

    @chunks.setter
    def chunks(self, chunks):
        self._chunks = chunks
        if chunks is not None:
            self._parametersWidget.verticalChunkSize.setText(str(chunks[0]))
            self._parametersWidget.horizontalChunkSize.setText(str(chunks[1]))

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, background):
        if self._parametersWidget.bsBackgroundCB.findText(background) >= 0:
            self._background = background
            self._parametersWidget.bsBackgroundCB.setCurrentText(background)

    @property
    def bottom_threshold(self):
        return self._bottom_threshold

    @bottom_threshold.setter
    def bottom_threshold(self, bottom):
        self._bottom_threshold = bottom
        self._parametersWidget.bottomLE.setText(bottom)

    @property
    def top_threshold(self):
        return self._top_threshold

    @top_threshold.setter
    def top_threshold(self, top):
        self._top_threshold = top
        self._parametersWidget.topLE.setText(top)

    @property
    def _dataset(self):
        return self._input_dataset

    @_dataset.setter
    def _dataset(self, dataset):
        self._input_dataset = dataset
        self.__clearMaskWithWrongShape()

    @property
    def mask(self):
        return self._svPlotWidget.getSelectionMask()

    @mask.setter
    def mask(self, mask):
        self.__storeMask(mask)
        self.__clearMaskWithWrongShape()

    def __storeMask(self, mask):
        if mask is None:
            self._svPlotWidget.clearMask()
        else:
            self._svPlotWidget.setSelectionMask(mask)

    @property
    def _svPlotWidget(self):
        return self._sv.getPlotWidget()

    def __clearMaskWithWrongShape(self):
        mask = self.mask
        if mask is None:
            return
        if self._dataset is None or self._dataset.data is None:
            return
        stack_shape = self._dataset.data.shape[-2:]
        mask_shape = mask.shape
        if stack_shape == mask_shape:
            return
        self.__storeMask(mask)
