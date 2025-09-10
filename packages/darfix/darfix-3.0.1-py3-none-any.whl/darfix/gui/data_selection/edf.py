from __future__ import annotations

import logging
import os
from typing import Optional

from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt
from silx.gui.dialog.DataFileDialog import DataFileDialog
from silx.io.url import DataUrl

from darfix import dtypes

from .DataSelectionBase import DataSelectionBase

_logger = logging.getLogger(__file__)


class EDFDatasetSelectionWidget(DataSelectionBase):
    """
    Widget that creates a dataset from a list of files or from a single filename.
    It lets the user add the first filename of a directory of files, or to
    upload manually each of the files to be read.
    If both options are filled up, only the files in the list of filenames
    are read.
    """

    sigProgressChanged = qt.Signal(int)

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)

        self._rawFilenameData.filenameChanged.connect(self.sigRawDataInfosChanged)
        self._rawFilesData.sigFilesChanged.connect(self.sigRawDataInfosChanged)
        self._onDiskCB.toggled.connect(self.sigRawDataInfosChanged)
        self._titleLE.editingFinished.connect(self.sigRawDataInfosChanged)

        assert isinstance(self._darkDataWidget, FilenameSelectionWidget)
        self._darkDataWidget.filenameChanged.connect(self.sigDarkDataInfosChanged)

    def _updateDataset(self, dataset):
        self._dataset = dataset

    def buildRawDataWidget(self):
        self._rawFilenameData = FilenameSelectionWidget(parent=self)
        self._rawFilesData = FilesSelectionWidget(parent=self)
        self._onDiskCB = qt.QCheckBox("Keep data on disk", self)
        titleWidget = qt.QWidget(self)
        titleLayout = qt.QHBoxLayout()
        titleLabel = qt.QLabel("Workflow title:")
        self._titleLE = qt.QLineEdit("")
        titleLayout.addWidget(titleLabel)
        titleLayout.addWidget(self._titleLE)
        titleWidget.setLayout(titleLayout)
        rawData = qt.QWidget(self)
        rawData.setLayout(qt.QVBoxLayout())
        rawData.layout().addWidget(titleWidget)
        rawData.layout().addWidget(self._rawFilenameData)
        rawData.layout().addWidget(self._rawFilesData)
        rawData.layout().addWidget(self._onDiskCB)
        rawData.layout().addWidget(titleWidget)
        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        rawData.layout().addWidget(spacer)

        return rawData

    def buildDarkDataWidget(self):
        return FilenameSelectionWidget(parent=self)

    @property
    def dataset(self):
        return self._dataset

    def getDataset(self) -> dtypes.Dataset:
        return dtypes.Dataset(
            dataset=self._dataset,
            indices=self.indices,
            bg_indices=self.bg_indices,
            bg_dataset=self.bg_dataset,
        )

    def updateProgress(self, progress):
        self.sigProgressChanged.emit(progress)

    def setRawFilename(self, filename):
        self._rawFilenameData.setFilename(filename=filename)
        self.sigRawDataInfosChanged.emit()

    def keepDataOnDisk(self) -> bool:
        return self._onDiskCB.isChecked()

    def setKeepDataOnDisk(self, on_disk: bool):
        self._onDiskCB.setChecked(on_disk)
        self.sigRawDataInfosChanged.emit()

    # expose API
    def getRawFilenames(self) -> list:
        return self._rawFilesData.getFiles()

    def getRawFilename(self) -> str:
        return self._rawFilenameData.getFilename()

    def getDarkFilename(self) -> str:
        return self._darkDataWidget.getFilename()

    def setRawFilenames(self, files):
        self._rawFilesData.setFiles(files)
        self.sigRawDataInfosChanged.emit()

    def setDarkFilename(self, filename: str):
        self._darkDataWidget.setFilename(filename)
        self.sigDarkDataInfosChanged.emit()

    def getTreatedDir(self) -> str:
        return self._treatedDirData.getDir()

    def setTreatedDir(self, _dir):
        self._treatedDirData.setDir(_dir)

    def getWorkflowTitle(self) -> str:
        return self._titleLE.text()

    def setWorkflowTitle(self, title: str) -> None:
        self._titleLE.setText(title)
        self.sigRawDataInfosChanged.emit()


class FilesSelectionWidget(qt.QWidget):
    """
    Widget used to get one or more files from the computer and add them to a list.
    """

    sigFilesChanged = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self._files = []

        self.setLayout(qt.QVBoxLayout())
        self._table = self._init_table()
        self._addButton = qt.QPushButton("Add")
        self._rmButton = qt.QPushButton("Remove")
        self.layout().addWidget(self._table)
        self.layout().addWidget(self._addButton)
        self.layout().addWidget(self._rmButton)
        self._addButton.clicked.connect(self._addFiles)
        self._rmButton.clicked.connect(self._removeFiles)

    def _init_table(self):
        table = qt.QTableWidget(0, 1, parent=self)
        table.horizontalHeader().hide()
        # Resize horizontal header to fill all the column size
        if hasattr(table.horizontalHeader(), "setSectionResizeMode"):  # Qt5
            table.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
        else:  # Qt4
            table.horizontalHeader().setResizeMode(0, qt.QHeaderView.Stretch)

        return table

    def _addFiles(self):
        """
        Opens the file dialog and let's the user choose one or more files.
        """
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.ExistingFiles)

        if not dialog.exec():
            dialog.close()
            return

        for file in dialog.selectedFiles():
            with block_signals(self):
                self.addFile(file)
        self.sigFilesChanged.emit()

    def _removeFiles(self):
        """
        Removes the selected items from the table.
        """
        selectedItems = self._table.selectedItems()
        if selectedItems is not None:
            for item in selectedItems:
                self._files.remove(item.text())
                self._table.removeRow(item.row())
        self.sigFilesChanged.emit()

    def addFile(self, file):
        """
        Adds a file to the table.

        :param str file: filepath to add to the table.
        """
        if not os.path.isfile(file):
            raise FileNotFoundError(file)
        item = qt.QTableWidgetItem()
        item.setText(file)
        row = self._table.rowCount()
        self._table.setRowCount(row + 1)
        self._table.setItem(row, 0, item)
        self._files.append(file)
        self.sigFilesChanged.emit()

    def getFiles(self):
        return self._files

    def setFiles(self, files):
        """
        Adds a list of files to the table.

        :param array_like files: List to add
        """
        for file in files:
            self.addFile(file)

    def getDir(self):
        if len(self._files):
            return os.path.dirname(self._files[0])
        return None


class DataPathSelection(qt.QWidget):
    """
    Widget to select a data path from a file path
    """

    def __init__(self, parent=None, text="data path") -> None:
        super().__init__(parent)
        self.__filePath = None

        self.setLayout(qt.QHBoxLayout())
        self._label = qt.QLabel(text, self)
        self.layout().addWidget(self._label)
        self._dataPathQLE = qt.QLineEdit("", self)
        self.layout().addWidget(self._dataPathQLE)
        self._selectPB = qt.QPushButton("select", self)
        self.layout().addWidget(self._selectPB)

        # connect signal / slot
        self._selectPB.released.connect(self._selectDataPath)

    def getDataPath(self):
        return self._dataPathQLE.text()

    def setDataPath(self, dataPath: str):
        try:
            url = DataUrl(path=dataPath)
        except Exception:
            self._dataPathQLE.setText(str(dataPath))
        else:
            self._dataPathQLE.setText(url.data_path())

    def setHDF5File(self, filename: str):
        """
        set file name. Warning according to existing architecture the file name
        can either be the file name directly or a DataUrl as a str
        """
        try:
            # handle case getRawFilename return the url and not the file path only
            url = DataUrl(path=filename)
        except Exception:
            pass
        else:
            filename = url.file_path()
        self.__filePath = filename

    def _selectDataPath(self):
        """callback when want to select a data path"""
        if self.__filePath is None:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Critical)
            msg.setText("Please select the HDF5 file containing data first")
            msg.setStandardButtons(qt.QMessageBox.Ok)
            msg.exec()
        else:
            from silx.gui.dialog.GroupDialog import GroupDialog

            dialog = GroupDialog(parent=self)
            dialog.addFile(self.__filePath)
            dialog.setMode(GroupDialog.LoadMode)
            if dialog.exec():
                selectedUrl = dialog.getSelectedDataUrl()
                if selectedUrl is not None:
                    self._dataPathQLE.setText(selectedUrl.data_path())

    def getMetadataUrl(self) -> Optional[DataUrl]:
        """
        Return the path to the data url
        """
        if self.getDataPath() == "":
            return None
        else:
            return DataUrl(
                file_path=self.__filePath,
                data_path=self.getDataPath(),
                scheme="silx",
            )


class FilenameSelectionWidget(qt.QWidget):
    """
    Widget used to obtain a filename (manually or from a file)
    """

    filenameChanged = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self._isH5 = False
        self._filename = None
        self._filenameLE = qt.QLineEdit("", parent=self)
        self._addButton = qt.QPushButton("Upload data", parent=self)
        # self._okButton =  qt.QPushButton("Ok", parent=self)
        self._addButton.pressed.connect(self._uploadFilename)
        # self._okButton.pressed.connect(self.close)
        self.setLayout(qt.QHBoxLayout())

        self.layout().addWidget(self._filenameLE)
        self.layout().addWidget(self._addButton)
        # self.layout().addWidget(self._okButton)

    def isHDF5(self, isH5):
        self._isH5 = isH5

    def _uploadFilename(self):
        """
        Loads the file from a FileDialog.
        """
        if self._isH5:
            fileDialog = DataFileDialog()
            fileDialog.setFilterMode(DataFileDialog.FilterMode.ExistingDataset)
            if self._filename:
                fileDialog.selectUrl(self._filename)
            if fileDialog.exec():
                self._filename = fileDialog.selectedDataUrl().path()
                self._filenameLE.setText(self._filename)
                self.filenameChanged.emit()
            else:
                _logger.warning("Could not open file")
        else:
            fileDialog = qt.QFileDialog()
            fileDialog.setFileMode(qt.QFileDialog.ExistingFile)
            if self._filename:
                fileDialog.selectFile(self._filename)
            if fileDialog.exec():
                self._filenameLE.setText(fileDialog.selectedFiles()[0])
                self._filename = fileDialog.selectedFiles()[0]
                self.filenameChanged.emit()
            else:
                _logger.warning("Could not open file")

    def getFilename(self):
        return str(self._filenameLE.text())

    def setFilename(self, filename):
        self._filename = filename
        self._filenameLE.setText(str(filename))
