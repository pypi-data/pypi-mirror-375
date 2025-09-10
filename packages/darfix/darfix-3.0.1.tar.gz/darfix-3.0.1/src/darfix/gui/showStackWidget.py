__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "03/12/2020"

import glob
import os

from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot.StackView import StackViewMainWindow
from silx.io import fabioh5
from silx.io.url import DataUrl

import darfix
from darfix.core.dataset import Data

from .data_selection.WorkingDirSelectionWidget import WorkingDirSelectionWidget


class ShowStackWidget(qt.QMainWindow):
    """
    Widget to show a stack of data
    """

    sigComputed = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        layout = qt.QVBoxLayout()
        self._filenameData = WorkingDirSelectionWidget(parent=self)
        self._filenameData.dirChanged.connect(self.updateStack)
        layout.addWidget(self._filenameData)
        self._sv = StackViewMainWindow()
        self._sv.setColormap(
            Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME, normalization="linear")
        )
        self._sv.setKeepDataAspectRatio(True)
        self._sv.hide()
        layout.addWidget(self._sv)
        widget = qt.QWidget(parent=self)
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def updateStack(self):
        """
        Update stack with new first filename
        """
        _dir = self._filenameData.getDir()
        data_urls = []
        metadata = []
        for filename in sorted(glob.glob(os.path.join(_dir, "*"))):
            if os.path.isfile(filename):
                data_urls.append(DataUrl(file_path=filename, scheme="fabio"))
                metadata.append(fabioh5.EdfFabioReader(file_name=filename))

        data = Data(urls=data_urls, metadata=metadata, in_memory=False)

        self._sv.setStack(data)
        self._sv.show()
