from __future__ import annotations

from ewokscore.missing_data import MISSING_DATA
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread

from darfix.gui.zSumWidget import ZSumWidget
from darfix.tasks.zsum import ZSum


class ZSumWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=ZSum):
    """
    Widget that compute and display the Z-sum of a dataset
    """

    name = "z sum"
    icon = "icons/zsum.svg"
    want_main_area = True
    want_control_area = False

    _ewoks_inputs_to_hide_from_orange = ("indices", "dimension")

    def __init__(self):
        super().__init__()

        self._widget = ZSumWidget(parent=self)
        self.mainArea.layout().addWidget(self._widget)
        # connect signal / slot
        self._widget.sigFilteringRequested.connect(self._filterStack)
        self._widget.sigResetFiltering.connect(self._resetFilterStack)

    def handleNewSignals(self) -> None:
        dataset = self.get_task_input_value("dataset", None)
        dimension = self.get_task_input_value("dimension", None)
        if dataset is None:
            return super().handleNewSignals()

        # Do not use default dimension if number of dims do not match
        if dimension and len(dataset.dataset.dims) != len(dimension):
            self.set_default_input("dimension", None)
            dimension = None

        self._widget.setDataset(dataset, dimension)
        self.open()
        return super().handleNewSignals()

    def task_output_changed(self):
        z_sum = self.get_task_output_value("zsum", MISSING_DATA)
        if z_sum is not MISSING_DATA:
            self._widget.setZSum(z_sum)

    def _filterStack(self, dimension_index: int, value_index: int):
        self.set_default_input("indices", self._widget.indices)
        self.set_default_input("dimension", (dimension_index, value_index))
        self.execute_ewoks_task()

    def _resetFilterStack(self):
        self.set_default_input("indices", None)
        self.set_default_input("dimension", None)
        self.execute_ewoks_task()
