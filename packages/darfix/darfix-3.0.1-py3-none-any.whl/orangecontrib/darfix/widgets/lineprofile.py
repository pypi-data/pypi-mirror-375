__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "20/11/2020"

from ewoksorange.bindings.owwidgets import OWWidget

from darfix.gui.lineProfileWidget import LineProfileWidget


class LineProfileWidgetOW(OWWidget):
    """
    Widget that can display a line from an image.

    This widget have no input / output and setting the image must be done manually.
    """

    name = "line profile"
    icon = "icons/line_profile.png"
    want_main_area = False

    def __init__(self):
        super().__init__()

        self._widget = LineProfileWidget(parent=self)
        self.controlArea.layout().addWidget(self._widget)
