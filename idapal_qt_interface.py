"""
summary: adding PySide6 widgets into an `ida_kernwin.PluginForm`

description:
  Using `ida_kernwin.PluginForm.FormToPySideWidget`, this script
  converts IDA's own dockable widget into a type that is
  recognized by PySide6 (Qt6), which then enables populating it with
  regular Qt widgets.

  IDA Pro 9.3 ships Qt6 / PySide6. PyQt5 is no longer available.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QScrollArea
from PySide6.QtGui import QPalette, QColor
import textwrap

import ida_kernwin, ida_hexrays, ida_funcs, ida_name, ida_bytes

example_input = {'function_name': 'ExampleName', 'comment': "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque orci odio, feugiat nec nisi vel, tempus laoreet nunc. Aliquam libero felis, lacinia non imperdiet sit amet, volutpat vitae odio. Phasellus in ligula sit amet nibh posuere malesuada vel sit amet dui. Donec gravida nec elit vitae mollis. Donec sollicitudin, mauris pellentesque tempus sodales, velit orci tempor sapien, at rutrum urna tellus vel mauris. Donec ac rhoncus nisi, vel consequat libero. In dictum neque ligula, sit amet ultricies eros facilisis eu. Donec justo leo, suscipit quis ligula ut, blandit venenatis neque. Duis euismod viverra tellus, quis dapibus purus facilisis condimentum. Donec massa augue, vestibulum nec ipsum vulputate, feugiat volutpat mi. Sed nec nisl ex. Aliquam dapibus ligula ac orci hendrerit, id sodales leo tempus. Aenean vehicula metus vel pellentesque suscipit. Etiam vel dictum massa. Proin vitae varius sapien. Maecenas accumsan nulla rhoncus ipsum consequat, eget commodo sem finibus. Sed sed metus urna. Praesent vel nulla sed nunc feugiat fermentum a a tortor. Etiam auctor sit amet ligula eu tristique. Suspendisse sollicitudin, sem ut tincidunt volutpat, ipsum risus cursus nisl, non aliquet arcu ipsum eget massa. Fusce venenatis, leo eleifend luctus ultrices, quam odio fringilla augue, vitae tempus purus massa eu nulla. Cras a ullamcorper ligula.", 'variables': [{'original_name': 'a1', 'new_name': 'example1'}, {'original_name': 'a2', 'new_name': 'example2'}, {'original_name': 'a3', 'new_name': 'example3'}]}

# ---------------------------------------------------------------------------
# Qt6 alignment / check-state helpers
# In Qt6 the scoped enum values live under their class (AlignmentFlag,
# CheckState, etc.) but Qt also keeps the old un-scoped names as aliases on
# Qt.  We normalise everything to the scoped form so the code is forward-safe.
# ---------------------------------------------------------------------------
AlignLeft    = QtCore.Qt.AlignmentFlag.AlignLeft
AlignVCenter = QtCore.Qt.AlignmentFlag.AlignVCenter
AlignTop     = QtCore.Qt.AlignmentFlag.AlignTop
Checked      = QtCore.Qt.CheckState.Checked


class FunctionNameWidget(QWidget):
    accepted = True

    def __init__(self, function_name):
        super(FunctionNameWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(AlignLeft | AlignVCenter)

        group_box = QtWidgets.QGroupBox("aiDAPal Function Name")
        group_layout = QtWidgets.QHBoxLayout()
        group_layout.setAlignment(AlignLeft | AlignVCenter)
        group_layout.setSpacing(10)

        checkbox = QtWidgets.QCheckBox()
        checkbox.setCheckState(Checked)
        checkbox.stateChanged.connect(self.accepted_state_change)

        group_layout.addWidget(checkbox)
        group_layout.addWidget(QtWidgets.QLabel(function_name))

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def accepted_state_change(self, state):
        print(f'Accepted: {state == Checked}')
        self.accepted = (state == Checked)


class CommentWidget(QWidget):
    accepted = True

    def __init__(self, comment):
        super(CommentWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(AlignLeft | AlignVCenter)

        group_box = QtWidgets.QGroupBox("aiDAPal Comment")
        group_layout = QtWidgets.QHBoxLayout()
        group_layout.setAlignment(AlignLeft | AlignVCenter)
        group_layout.setSpacing(10)

        checkbox = QtWidgets.QCheckBox()
        checkbox.setCheckState(Checked)
        checkbox.stateChanged.connect(self.accepted_state_change)

        comment_area = QtWidgets.QLabel(comment)
        comment_area.setWordWrap(True)
        comment_area.setMinimumWidth(500)

        # Wrap the comment_area in a QScrollArea
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(comment_area)

        group_layout.addWidget(checkbox)
        group_layout.addWidget(scroll_area)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def accepted_state_change(self, state):
        print(f'Accepted: {state == Checked}')
        self.accepted = (state == Checked)


class VariableWidget(QWidget):
    accepted = True

    def __init__(self, variables):
        super(VariableWidget, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(AlignLeft | AlignVCenter)

        group_box = QtWidgets.QGroupBox("aiDAPal Variables")
        group_box_layout = QtWidgets.QVBoxLayout()

        group_layout = QtWidgets.QGridLayout()
        group_layout.setAlignment(AlignLeft | AlignVCenter)
        group_layout.setSpacing(10)
        self.checkboxes = []

        columns = 3
        for i in range(len(variables)):
            row = i // columns
            col = (i % columns) * 3  # checkbox, original_name, new_name

            original_name = variables[i].get('original_name', '')
            new_name = variables[i].get('new_name', '')
            if not original_name and not new_name:
                continue
            checkbox = QtWidgets.QCheckBox()
            checkbox.setCheckState(Checked)
            checkbox.stateChanged.connect(self.accepted_state_change)
            self.checkboxes.append(checkbox)

            frame = QtWidgets.QFrame()
            # Qt6: Panel and Raised are on QFrame.Shape / QFrame.Shadow
            frame.setFrameShape(QtWidgets.QFrame.Shape.Panel)
            frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
            frame_layout = QtWidgets.QHBoxLayout()
            frame_layout.addWidget(checkbox)
            frame_layout.addWidget(QtWidgets.QLabel(original_name))
            frame_layout.addWidget(QtWidgets.QLabel(new_name))
            frame.setLayout(frame_layout)
            group_layout.addWidget(frame, row, col)

        scroll_widget = QtWidgets.QWidget()
        scroll_widget.setLayout(group_layout)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        group_box_layout.addWidget(scroll_area)
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def accepted_state_change(self, state):
        print(f'Accepted: {state == Checked}')
        self.accepted = (state == Checked)

    def get_states(self):
        return [checkbox.isChecked() for checkbox in self.checkboxes]


class aiDAPalUIForm(ida_kernwin.PluginForm):

    ida_pal_results = None
    current_func = None
    current_data = None

    def __init__(self, ida_pal_results, current_func, current_data):
        super(aiDAPalUIForm, self).__init__()
        self.ida_pal_results = ida_pal_results
        self.current_func = current_func
        self.current_data = current_data

    def OnCreate(self, form):
        """
        Called when the widget is created.

        IDA Pro 9.3 has two TWidget conversion helpers:
          - FormToPySideWidget  calls QWidget.FromCapsule() which does NOT
            exist in the installed PySide6 — broken.
          - FormToPyQtWidget    calls shiboken6.Shiboken.wrapInstance() with
            PySide6.QtWidgets.QWidget — works correctly despite the name.
        """
        self.parent = self.FormToPyQtWidget(form)
        self.PopulateForm()

    def PopulateForm(self):
        function_name = self.ida_pal_results.get('function_name', '')
        comment       = self.ida_pal_results.get('comment', '')
        variables     = self.ida_pal_results.get('variables', [])

        # Use a container widget so setLayout always works regardless of
        # whether the IDA parent TWidget already has a layout on it.
        container = QtWidgets.QWidget()
        layout1 = QtWidgets.QVBoxLayout(container)

        if function_name:
            fn_widget = FunctionNameWidget(function_name)
            layout1.addWidget(fn_widget)
        if comment:
            cmt_widget = CommentWidget(comment)
            layout1.addWidget(cmt_widget)
        if variables:
            var_widget = VariableWidget(variables)
            layout1.addWidget(var_widget)

        accept_button = QtWidgets.QPushButton("Accept")
        cancel_button = QtWidgets.QPushButton("Cancel")

        layout1.addStretch()
        accept_button.clicked.connect(self.on_accept_clicked)
        cancel_button.clicked.connect(self.on_cancel_clicked)
        layout1.addWidget(accept_button)
        layout1.addWidget(cancel_button)

        outer = QtWidgets.QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        self.parent.setLayout(outer)

    def _get_inner_layout(self):
        container = self.parent.layout().itemAt(0).widget()
        return container.layout()

    def get_variable_states(self):
        state_values = []
        layout = self._get_inner_layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, VariableWidget):
                state_values.extend(widget.get_states())
        return state_values

    def get_comment_state(self):
        layout = self._get_inner_layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, CommentWidget):
                return widget.accepted
        return True

    def get_function_name_state(self):
        layout = self._get_inner_layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FunctionNameWidget):
                return widget.accepted
        return True

    def on_accept_clicked(self):
        vstates = self.get_variable_states()
        variables = self.ida_pal_results.get('variables', [])
        valid = [var for var in variables if var.get('original_name') or var.get('new_name')]
        for var, state in zip(valid, vstates):
            var["accepted"] = state
            if state:
                print(f'{var.get("original_name", "")} -> {var.get("new_name", "")}: Accepted')

        if not self.get_comment_state():
            self.ida_pal_results["comment"] = None
        if not self.get_function_name_state():
            self.ida_pal_results["function_name"] = None

        print(self.ida_pal_results)
        self.do_update()

    def do_update(self):
        new_cmt = ''
        new_name = None
        comment = self.ida_pal_results.get("comment")
        if comment:
            new_cmt = '\n'.join(textwrap.wrap(comment, width=80))
            if self.current_func:
                cf = ida_funcs.get_func(self.current_func.entry_ea)
                ida_funcs.set_func_cmt(cf, new_cmt, False)
            if self.current_data:
                ida_bytes.set_cmt(self.current_data, new_cmt, False)

        # skip rename if model returned an IDA auto-generated name
        _IDA_PREFIXES = ('sub_', 'loc_', 'byte_', 'word_', 'dword_', 'qword_',
                         'unk_', 'off_', 'seg_', 'asc_', 'str_', 'nullsub_')
        function_name = self.ida_pal_results.get("function_name")
        if function_name and self.current_func:
            if any(function_name.lower().startswith(p) for p in _IDA_PREFIXES):
                print(f'aiDAPal: skipping rename, model returned auto-generated name: {function_name}')
            else:
                new_name = f"{function_name}_{hex(self.current_func.entry_ea)[2:]}"
                print(f'Trying function name update {new_name}')
                if ida_name.set_name(self.current_func.entry_ea, new_name, ida_name.SN_CHECK):
                    print('successfully updated name')

        for var in self.ida_pal_results.get('variables', []):
            if var.get('accepted'):
                orig = var.get('original_name', '')
                new  = var.get('new_name', '')
                if self.current_func and orig and new:
                    print(f"trying function var - {orig} - {new}")
                    if ida_hexrays.rename_lvar(self.current_func.entry_ea, orig, new):
                        print(f"Updated function var - {orig} - {new}")
                if self.current_data and new:
                    ida_name.set_name(self.current_data, new, ida_name.SN_CHECK)
                    print(f"trying data var - {orig} - {new}")

        if self.current_func:
            self.current_func.refresh_func_ctext()
        self.Close(0)

    def on_cancel_clicked(self):
        self.Close(0)

    def OnClose(self, form):
        """
        Called when the widget is closed.
        """
        pass


class aiDAPalUI:
    def __init__(self, ida_pal_results=None, cur_func=None, cur_data=None):
        if ida_pal_results is None:
            self.ida_pal_results = example_input
        else:
            self.ida_pal_results = ida_pal_results
        self.plg = aiDAPalUIForm(self.ida_pal_results, cur_func, cur_data)
        self.plg.Show("aiDAPal Results")
