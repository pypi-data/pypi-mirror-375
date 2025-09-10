from __future__ import annotations

import numpy
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D

from ..dtypes import AxisAndValueIndices
from ..dtypes import Dataset
from .chooseDimensions import ChooseDimensionDock
from .chooseDimensions import ChooseDimensionWidget


class ZSumWidget(qt.QMainWindow):
    sigFilteringRequested = qt.Signal(list, list)
    sigResetFiltering = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self._plot = Plot2D(parent=self)
        self._plot.setDefaultColormap(Colormap(name="viridis", normalization="linear"))
        self._chooseDimensionDock = ChooseDimensionDock(self)
        self._chooseDimensionDock.hide()
        self._chooseDimensionDock.widget.filterChanged.connect(
            self.sigFilteringRequested
        )
        self._chooseDimensionDock.widget.stateDisabled.connect(self.sigResetFiltering)
        layout = qt.QVBoxLayout()
        layout.addWidget(self._plot)
        layout.addWidget(self._chooseDimensionDock)
        widget = qt.QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def setDataset(
        self, dataset: Dataset, dimension: AxisAndValueIndices | None = None
    ):
        self.dataset = dataset.dataset
        self.indices = dataset.indices
        if len(self.dataset.data.shape) > 3:
            self._chooseDimensionDock.show()
            self._chooseDimensionDock.widget.setDimensions(self.dataset.dims)
            if dimension is not None:
                widget: ChooseDimensionWidget = self._chooseDimensionDock.widget
                widget.setDimension(dimension)
        self._plot.setKeepDataAspectRatio(True)
        self._plot.setGraphTitle(self.dataset.title)

    def setZSum(self, zsum):
        self._addImage(zsum)

    def _addImage(self, image):
        if self.dataset.transformation is None:
            self._plot.addImage(image, xlabel="pixels", ylabel="pixels")
            return
        if self.dataset.transformation.rotate:
            image = numpy.rot90(image, 3)
        self._plot.addImage(
            image,
            origin=self.dataset.transformation.origin,
            scale=self.dataset.transformation.scale,
            xlabel=self.dataset.transformation.label,
            ylabel=self.dataset.transformation.label,
        )

    def setColormap(self, colormap: Colormap):
        self._plot.setDefaultColormap(colormap)
