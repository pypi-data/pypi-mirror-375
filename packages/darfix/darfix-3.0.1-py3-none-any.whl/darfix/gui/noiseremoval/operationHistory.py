from __future__ import annotations

from silx.gui import qt

from ...core.noiseremoval import NoiseRemovalOperation


class OperationHistoryWidget(qt.QWidget):
    """Keeps the history of noise removal operations and displays them in a QListWidget"""

    sigHistoryChanged = qt.Signal(list)

    def __init__(self, parent: qt.QWidget | None = None) -> None:
        super().__init__(parent)

        layout = qt.QVBoxLayout()
        assert layout is not None
        self._listWidget = qt.QListWidget()
        self._listWidget.setSelectionMode(
            qt.QAbstractItemView.SelectionMode.NoSelection
        )
        self._listWidget.hide()
        self._checkbox = qt.QCheckBox("Show history")

        layout.addWidget(self._checkbox)
        layout.addWidget(self._listWidget)
        self.setLayout(layout)

        self._checkbox.toggled.connect(self._listWidget.setVisible)
        self._checkbox.setChecked(True)

        self._operations: list[NoiseRemovalOperation] = []

    def append(self, operation: NoiseRemovalOperation):
        self._operations.append(operation)
        operation_order = len(self._operations)
        self._listWidget.addItem(
            qt.QListWidgetItem(f"{operation_order}: {str(operation)}")
        )
        self.sigHistoryChanged.emit(self._operations)

    def pop(self):
        self._operations.pop()
        self._listWidget.takeItem(self._listWidget.count() - 1)
        self.sigHistoryChanged.emit(self._operations)

    def clear(self):
        self._operations.clear()
        self._listWidget.clear()
        self.sigHistoryChanged.emit(self._operations)

    def getHistory(self):
        return list(self._operations)

    def setHistory(self, operations: list[NoiseRemovalOperation]):
        self._operations = operations
        self._listWidget.clear()
        for order, operation in enumerate(operations):
            self._listWidget.addItem(qt.QListWidgetItem(f"{order}: {str(operation)}"))
        self.sigHistoryChanged.emit(self._operations)
