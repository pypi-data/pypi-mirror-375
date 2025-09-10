from __future__ import annotations

import logging

import numpy
from ewoksorange.gui.parameterform import block_signals
from silx.gui import qt
from silx.gui.colors import Colormap
from silx.gui.plot import Plot2D
from silx.gui.plot import StackView
from silx.image.marchingsquares import find_contours
from silx.io.dictdump import dicttonx

import darfix

from ... import dtypes
from ...core.dataset import Operation
from ...core.rocking_curves import MAPS_1D
from ...core.rocking_curves import MAPS_2D
from ...core.rocking_curves import fit_2d_rocking_curve
from ...core.rocking_curves import fit_rocking_curve
from ...core.rocking_curves import generate_rocking_curves_nxdict
from ...core.utils import NoDimensionsError
from ...core.utils import TooManyDimensionsForRockingCurvesError
from ..utils.message import missing_dataset_msg
from .fitComboBox import FitComboBox

_logger = logging.getLogger(__file__)


# "Residuals" are not given by the fit but computed by the widget.
# It needs to be handled separately of other `MAPS` values
MAPS_CB_OPTIONS_1D = [*MAPS_1D, "Residuals"]
MAPS_CB_OPTIONS_2D = [*MAPS_2D, "Residuals"]


def _get_option_label(item: str, dataset: dtypes.ImageDataset):
    if "first motor" in item:
        return item.replace("first motor", dataset.dims.get(0).name)

    if "second motor" in item:
        return item.replace("second motor", dataset.dims.get(1).name)

    return item


class RockingCurvesWidget(qt.QMainWindow):
    """
    Widget to apply fit to a set of images and plot the amplitude, fwhm, peak position, background and residuals maps.
    """

    sigFitClicked = qt.Signal()

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        self.dataset = None
        self.indices = None
        self._update_dataset = None
        self._residuals_cache = None
        self.maps = None
        """ Holds the result of the fit as as a stack of maps"""

        widget = qt.QWidget(parent=self)
        layout = qt.QGridLayout()

        self._sv = StackView(parent=self, position=True)
        self._sv.setKeepDataAspectRatio(True)
        self._sv.setColormap(Colormap(name=darfix.config.DEFAULT_COLORMAP_NAME))
        self._plot = Plot2D(parent=self)
        self._plot.setDefaultColormap(
            Colormap(
                name=darfix.config.DEFAULT_COLORMAP_NAME,
                normalization=darfix.config.DEFAULT_COLORMAP_NORM,
            )
        )
        self._plot.setGraphTitle("Rocking curves")

        intLabel = qt.QLabel("Intensity threshold:")
        self._intensityThresholdLE = qt.QLineEdit("15")
        self._intensityThresholdLE.setValidator(qt.QDoubleValidator())

        self._computeFit = qt.QPushButton("Fit data")
        self._computeFit.clicked.connect(self._launchFit)
        self._fitMethodLabel = qt.QLabel("method")
        self._fitMethodCB = FitComboBox()

        self._abortFit = qt.QPushButton("Abort")
        self._abortFit.clicked.connect(self.__abort)
        self._motorValuesCheckbox = qt.QCheckBox("Use motor values")
        self._motorValuesCheckbox.setChecked(True)
        self._motorValuesCheckbox.stateChanged.connect(self._checkboxStateChanged)
        self._centerDataCheckbox = qt.QCheckBox("Center angle values")
        self._centerDataCheckbox.setEnabled(False)
        self._centerDataCheckbox.stateChanged.connect(self._checkboxStateChanged)
        self._parametersLabel = qt.QLabel("")
        self._plotMaps = Plot2D(self)
        self._plotMaps.setDefaultColormap(
            Colormap(name="cividis", normalization="linear")
        )
        self._plotMaps.hide()
        self._mapsCB = qt.QComboBox(self)
        self._mapsCB.hide()
        self._exportButton = qt.QPushButton("Export maps")
        self._exportButton.hide()
        self._exportButton.clicked.connect(self.exportMaps)

        layout.addWidget(self._sv, 0, 0, 1, 2)
        layout.addWidget(self._plot, 0, 2, 1, 3)
        layout.addWidget(self._parametersLabel, 1, 2, 1, 2)
        layout.addWidget(self._motorValuesCheckbox, 2, 2, 1, 1)
        layout.addWidget(self._centerDataCheckbox, 2, 3, 1, 1)
        layout.addWidget(intLabel, 3, 0, 1, 1)
        layout.addWidget(self._intensityThresholdLE, 3, 1, 1, 1)
        layout.addWidget(self._computeFit, 3, 2, 1, 1)
        layout.addWidget(self._fitMethodLabel, 3, 3, 1, 1)
        layout.addWidget(self._fitMethodCB, 3, 4, 1, 1)
        layout.addWidget(self._abortFit, 3, 2, 1, 2)
        layout.addWidget(self._mapsCB, 4, 0, 1, 4)
        layout.addWidget(self._plotMaps, 5, 0, 1, 4)
        layout.addWidget(self._exportButton, 6, 0, 1, 5)
        self._abortFit.hide()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # connect signal / slot
        self._mapsCB.currentTextChanged.connect(self._updatePlot)

    def setDataset(self, dataset: dtypes.Dataset):
        if not dataset.dataset.dims.ndim:
            raise NoDimensionsError("RockingCurvesWidget")
        self.dataset = dataset.dataset
        self.indices = dataset.indices
        self._update_dataset = dataset.dataset
        self._residuals_cache = None
        self.setStack()

        if self.dataset.dims.ndim == 1:
            options = MAPS_CB_OPTIONS_1D
        elif self.dataset.dims.ndim == 2:
            options = MAPS_CB_OPTIONS_2D
        else:
            raise TooManyDimensionsForRockingCurvesError()

        with block_signals(self._mapsCB):
            self._mapsCB.clear()
            for option in options:
                self._mapsCB.addItem(_get_option_label(option, dataset=dataset.dataset))

        self._sv.getPlotWidget().sigPlotSignal.connect(self._onClickOnStack)
        self._sv.sigFrameChanged.connect(self._addPoint)

        self._sv.setGraphTitle(dataset.dataset.title)

    def setStack(self, dataset=None):
        """
        Sets new data to the stack.
        Mantains the current frame showed in the view.

        :param Dataset dataset: if not None, data set to the stack will be from the given dataset.
        """
        if dataset is None:
            dataset = self.dataset
        nframe = self._sv.getFrameNumber()
        if self.indices is None:
            self._sv.setStack(dataset.get_data() if dataset is not None else None)
        else:
            self._sv.setStack(
                dataset.get_data(self.indices) if dataset is not None else None
            )
        self._sv.setFrameNumber(nframe)

    def _onClickOnStack(self, info):
        if info["event"] == "mouseClicked":
            # In case the user has clicked on a pixel in the stack
            data = self.dataset.get_data(self.indices)
            px = info["x"]
            py = info["y"]
            # Show vertical and horizontal lines for clicked pixel
            self._sv.getPlotWidget().addCurve(
                (px, px), (0, data.shape[1]), legend="x", color="r"
            )
            self._sv.getPlotWidget().addCurve(
                (0, data.shape[2]), (py, py), legend="y", color="r"
            )
            self._plotRockingCurves(px, py)

    def _addPoint(self, i=None):
        """
        Slot to add curve for frame number in rocking curves plot.

        :param int i: frame number
        """
        xc = self._sv.getPlotWidget().getCurve("x")
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve("y").getYData()[0]
            self._plotRockingCurves(px, py)

    def _computeContours(self, image, origin=None, scale=None):
        polygons = []
        levels = []
        for i in numpy.linspace(numpy.min(image), numpy.max(image), 10):
            polygons.append(find_contours(image, i))
            levels.append(i)
        # xdim = self.dataset.dims.get(1)
        # ydim = self.dataset.dims.get(0)
        for ipolygon, polygon in enumerate(polygons):
            # iso contours
            for icontour, contour in enumerate(polygon):
                if len(contour) == 0:
                    continue
                # isClosed = numpy.allclose(contour[0], contour[-1])
                x = contour[:, 1]
                y = contour[:, 0]
                if scale is not None:
                    x *= scale[0]
                    y *= scale[1]
                    x += origin[0] + scale[0] / 2
                    y += origin[1] + scale[1] / 2
                legend = "poly{}.{}".format(icontour, ipolygon)
                self._plot.addCurve(
                    x=x,
                    y=y,
                    linestyle="-",
                    linewidth=2.0,
                    legend=legend,
                    resetzoom=False,
                    color="w",
                )

    def _plotRockingCurves(self, px: float, py: float):
        """
        Plot rocking curves of data and fitted data at pixel (px, py).

        :param Data data: stack of images to plot
        :param px: x pixel
        :param py: y pixel
        """
        # Get rocking curves from data
        self._plot.clear()
        if self.dataset is None:
            return
        try:
            data = self.dataset.get_data(self.indices)
            if self.dataset.in_memory:
                y = data[:, int(py), int(px)]
            else:
                y = numpy.array([image[int(py), int(px)] for image in data])
        except IndexError:
            _logger.warning("Index out of bounds")
            return
        if self.dataset.dims.ndim == 2:
            image = numpy.zeros(self.dataset.nframes)
            image[self.indices] = y
            xdim = self.dataset.dims.get(1)
            ydim = self.dataset.dims.get(0)
            assert xdim is not None
            assert ydim is not None
            self._plot.remove(kind="curve")

            frameNumber = self._sv.getFrameNumber()
            dotx = int(frameNumber / ydim.size)
            doty = frameNumber % ydim.size

            xscale = xdim.step
            yscale = ydim.step
            if self._motorValuesCheckbox.isChecked():
                origin = [xdim.start, ydim.start]
                dotx = xdim.start + xdim.step * dotx
                doty = ydim.start + ydim.step * doty
            else:
                origin = (0.0, 0.0)
                if self._centerDataCheckbox.isChecked():
                    dotx -= int(xdim.size / 2)
                    doty -= int(ydim.size / 2)
                    origin = (
                        -xscale * int(xdim.size / 2),
                        -yscale * int(ydim.size / 2),
                    )
                dotx *= xscale
                doty *= yscale
            try:
                y_gauss, pars = fit_2d_rocking_curve(
                    (image, None),
                    x_values=[
                        self.dataset.get_metadata_values(key=ydim.name),
                        self.dataset.get_metadata_values(key=xdim.name),
                    ],
                    shape=(ydim.size, xdim.size),
                )
                if numpy.array_equal(y_gauss, image):
                    raise RuntimeError()
                y_gauss = numpy.reshape(y_gauss, (xdim.size, ydim.size)).T
                self._computeContours(y_gauss, origin, (xscale, yscale))
                self._parametersLabel.setText(
                    "PEAK_X:{:.3f} PEAK_Y:{:.3f} FWHM_X:{:.3f} FWHM_Y:{:.3f} AMP:{:.3f} CORR:{:.3f} BG:{:.3f}".format(
                        *pars
                    )
                )
            except (TypeError, RuntimeError):
                _logger.warning("Cannot fit")

            y = numpy.reshape(image, (xdim.size, ydim.size)).T
            self._plot.addImage(
                y,
                xlabel=xdim.name,
                ylabel=ydim.name,
                origin=origin,
                scale=(xscale, yscale),
            )
            self._plot.addCurve([dotx], [doty], symbol="o", legend="dot_o", color="b")
        elif self.dataset.dims.ndim == 1:
            dim = self.dataset.dims.get(0)
            assert dim is not None
            if self._motorValuesCheckbox.isChecked():
                self._plot.setGraphXLabel(dim.name)
                x = numpy.array(
                    self.dataset.get_metadata_values(key=dim.name, indices=self.indices)
                )
            else:
                self._plot.setGraphXLabel("Indices")
                scale = dim.step
                x = numpy.arange(data.shape[0]) * scale
                if self._centerDataCheckbox.isChecked():
                    x -= int(dim.size / 2)

            if self._centerDataCheckbox.isChecked():
                middle = (float(x[-1]) - float(x[0])) / 2
                # x = numpy.linspace(-middle, middle, len(x))
                x -= float(x[0]) + middle
            # Show rocking curves and fitted curve into plot
            self._plot.clear()
            self._plot.addCurve(x, y, legend="data", color="b")
            self._plot.setGraphYLabel("Intensity")
            i = self._sv.getFrameNumber()
            try:
                y_gauss, pars = fit_rocking_curve(
                    (numpy.array(y), None), x_values=x, num_points=1000
                )
                self._parametersLabel.setText(
                    "AMP:{:.3f} PEAK:{:.3f} FWHM:{:.3f} BG:{:.3f}".format(*pars)
                )
            except TypeError:
                y_gauss = y
                _logger.warning("Cannot fit")

            # Add curves (points) for stackview frame number
            x_gauss = numpy.linspace(x[0], x[-1], len(y_gauss))
            self._plot.addCurve(x_gauss, y_gauss, legend="fit", color="r")
            self._plot.addCurve([x[i]], [y[i]], symbol="o", legend="dot_o", color="b")
            i_gauss = i * int((len(y_gauss) - 1) / (len(x) - 1))
            self._plot.addCurve(
                [x_gauss[i_gauss]],
                [y_gauss[i_gauss]],
                symbol="o",
                legend="dot_fit",
                color="r",
            )
        else:
            raise TooManyDimensionsForRockingCurvesError()

    def _launchFit(self):
        """
        Method called when button for computing fit is clicked
        """
        if self.dataset is None:
            missing_dataset_msg()
            return

        self._computeFit.hide()
        self.sigFitClicked.emit()
        # TODO: Abort button is not working
        # self._abortFit.show()

    def _computeResiduals(self) -> numpy.ndarray | None:
        """Note: The computation is cached as long as the dataset is loaded."""
        if self.dataset is None:
            missing_dataset_msg()
            return

        if self._residuals_cache is not None:
            return self._residuals_cache

        self._residuals_cache = numpy.sqrt(
            numpy.subtract(
                self._update_dataset.zsum(self.indices), self.dataset.zsum(self.indices)
            )
            ** 2
        )
        return self._residuals_cache

    def _updatePlot(self, map_name: str):
        """
        :param map_name: Name of the map to display.
        """
        if self.dataset is None:
            return

        if self.maps is None:
            return

        title = self.dataset.title
        if title:
            graph_title = f"{title} - {map_name}"
        else:
            graph_title = map_name

        self._plotMaps.setKeepDataAspectRatio(True)
        self._plotMaps.setGraphTitle(graph_title)
        if map_name == "Residuals":
            self._addImage(self._computeResiduals())
            return

        self._addImage(self.maps[self._mapsCB.currentIndex()])

    def __abort(self):
        self._abortFit.setEnabled(False)
        self.dataset.stop_operation(Operation.FIT)

    def onFitFinished(self):
        self._abortFit.hide()
        self._computeFit.show()

    def updateDataset(self, dataset: dtypes.ImageDataset, maps: numpy.ndarray):
        self._update_dataset, self.maps = dataset, maps
        self._updatePlot(self._mapsCB.currentText())
        self._plotMaps.show()
        self._mapsCB.show()
        self._exportButton.show()

    def _wholeStack(self):
        self.setStack(self.dataset)
        self._addPoint()

    def _checkboxStateChanged(self):
        """
        Update widgets linked to the checkbox state
        """
        self._centerDataCheckbox.setEnabled(not self._motorValuesCheckbox.isChecked())
        xc = self._sv.getPlotWidget().getCurve("x")
        if xc:
            px = xc.getXData()[0]
            py = self._sv.getPlotWidget().getCurve("y").getYData()[0]
            self._plotRockingCurves(px, py)
            self._updatePlot(self._mapsCB.currentData())

    def getIntensityThreshold(self) -> str:
        return self._intensityThresholdLE.text()

    def setIntensityThreshold(self, value: str):
        self._intensityThresholdLE.setText(value)

    def getFitMethod(self) -> str:
        return self._fitMethodCB.currentText()

    def setFitMethod(self, value: str):
        self._fitMethodCB.setText(value)

    def exportMaps(self):
        """
        Creates dictionary with maps information and exports it to a nexus file
        """
        if self.dataset is None or self.maps is None:
            missing_dataset_msg()
            return

        fileDialog = qt.QFileDialog()

        fileDialog.setFileMode(fileDialog.AnyFile)
        fileDialog.setAcceptMode(fileDialog.AcceptSave)
        fileDialog.setOption(fileDialog.DontUseNativeDialog)
        fileDialog.setDefaultSuffix(".h5")
        if fileDialog.exec():
            nxdict = generate_rocking_curves_nxdict(
                dataset=self.dataset, maps=self.maps, residuals=self._computeResiduals()
            )
            dicttonx(nxdict, fileDialog.selectedFiles()[0])

    def _addImage(self, image):
        if self.dataset.transformation is None:
            self._plotMaps.addImage(image, xlabel="pixels", ylabel="pixels")
            return
        if self.dataset.transformation.rotate:
            image = numpy.rot90(image, 3)
        self._plotMaps.addImage(
            image,
            origin=self.dataset.transformation.origin,
            scale=self.dataset.transformation.scale,
            xlabel=self.dataset.transformation.label,
            ylabel=self.dataset.transformation.label,
        )
