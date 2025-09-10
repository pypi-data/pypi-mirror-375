__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "20/11/2020"

from ewoksorange.bindings.owwidgets import OWWidget

from darfix.gui.linkComponentsWidget import LinkComponentsWidget


class LinkComponentsWidgetOW(OWWidget):
    """
    Widget that compare two stacks of images. Each of these stacks represents the
    components of a dataset.

    This widget have no input / output and setting the image must be done manually.
    """

    name = "link components"
    icon = "icons/link.png"
    want_main_area = False

    def __init__(self):
        super().__init__()

        self._widget = LinkComponentsWidget(parent=self)
        self.controlArea.layout().addWidget(self._widget)
