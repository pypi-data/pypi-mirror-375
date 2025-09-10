__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "30/11/2020"


import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot1D
from silx.gui.plot import Plot2D

import darfix

from .data_selection.edf import FilenameSelectionWidget


class LineProfileWidget(qt.QMainWindow):
    """
    Widget that shows how the intensity looks like in a line profile.
    The user can choose a pixel and the intensity along its x axis is showed.
    """

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()
        self._filename = FilenameSelectionWidget(parent=self)
        self._filename.filenameChanged.connect(self.setImage)
        self._plot2d = Plot2D(parent=self)
        self._plot2d.setDefaultColormap(
            Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME, normalization="linear")
        )
        self._plot2d.sigPlotSignal.connect(self._mouseSignal)
        self._plot1d = Plot1D(parent=self)
        layout.addWidget(self._filename, 0, 0, 1, 2)
        layout.addWidget(self._plot2d, 1, 0)
        layout.addWidget(self._plot1d, 1, 1)
        widget.setLayout(layout)
        widget.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.setCentralWidget(widget)

    def setImage(self):
        """
        Set image
        """
        filename = self._filename.getFilename()
        self._image = numpy.load(filename)
        self._plot2d.addImage(self._image)

    def _mouseSignal(self, info):
        """
        Method called when a signal from the plot is called
        """
        if info["event"] == "mouseClicked":
            py = info["y"]
            self._plot2d.addCurve(
                (0, self._image.shape[1]), (py, py), legend="y", color="g"
            )
            line_profile = self._image[int(py), :]
            self._plot1d.addCurve(
                numpy.arange(len(line_profile)), line_profile, color="g"
            )
