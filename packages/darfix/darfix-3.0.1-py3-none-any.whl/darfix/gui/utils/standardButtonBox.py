from __future__ import annotations

from silx.gui import qt


class StandardButtonBox(qt.QDialogButtonBox):
    """
    A button box including standard buttons: Ok, Abort and Reset.

    The box has two states that can be changed by using the method `setIsComputing`:
        - setIsComputing(False), default: Ok/Reset enabled. Abort hidden
        - setIsComputing(True): Ok/Reset disabled. Abort visible.
    """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setStandardButtons(
            qt.QDialogButtonBox.Ok
            | qt.QDialogButtonBox.Abort
            | qt.QDialogButtonBox.Reset
        )

        self.abortButton.hide()

    @property
    def okButton(self):
        okButton = self.button(qt.QDialogButtonBox.Ok)
        assert okButton is not None
        return okButton

    @property
    def resetButton(self):
        resetButton = self.button(qt.QDialogButtonBox.Reset)
        assert resetButton is not None
        return resetButton

    @property
    def abortButton(self):
        abortButton = self.button(qt.QDialogButtonBox.Abort)
        assert abortButton is not None
        return abortButton

    def setIsComputing(self, isComputing: bool):
        self.okButton.setDisabled(isComputing)
        self.resetButton.setDisabled(isComputing)
        self.abortButton.setVisible(isComputing)
