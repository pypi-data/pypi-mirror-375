from __future__ import annotations

# from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThread
# from silx.gui import qt

# from darfix.gui.data_selection.line_edits import FileLineEdit
# from darfix.tasks.zsum import ZSum

# class ZSumWidgetOW(OWEwoksWidgetOneThread, ewokstaskclass=ZSum):
#     """
#     Widget that compute and display the Z-sum of a dataset
#     """

#     name = "z sum"
#     icon = "icons/zsum.svg"
#     want_main_area = True
#     want_control_area = False

#     _ewoks_inputs_to_hide_from_orange = ("indices", "dimension")

#     def __init__(self):
#         super().__init__()
#         layout = qt.QVBoxLayout()
#         layout.addWidget(qt.QLabel("Select file path"))

#         self.fileSelection = FileLineEdit()

#         types = qt.QDialogButtonBox.Ok
#         _buttons = qt.QDialogButtonBox(parent=self)
#         _buttons.setStandardButtons(types)
#         layout.addWidget(_buttons)

#         _buttons.accepted.connect(self._executeTask)

#         self.mainArea.setLayout(layout)

#     def handleNewSignals(self) -> None:
#         self.open()
#         return super().handleNewSignals()

#     def task_output_changed(self):
#         if self.task_succeeded:
#             self.propagate_downstream()
#             self.close()
