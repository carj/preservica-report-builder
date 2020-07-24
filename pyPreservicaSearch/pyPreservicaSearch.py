import platform
import subprocess
import sys

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Slot, QRunnable, QThreadPool, QObject, SIGNAL, SLOT
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QAbstractItemView, QDialog, QDialogButtonBox, QApplication, QProgressDialog, QComboBox, \
    QItemDelegate, QLineEdit, QTreeView
from pyPreservica import *


class CallBack(QObject):
    change_value = QtCore.Signal(int)
    max_value = QtCore.Signal(int)

    def __init__(self):
        QObject.__init__(self)
        self.progress = 0
        self.total = 0

    def __call__(self, value):
        t = value.split(":")
        self.total = int(t[1])
        self.progress = int(t[0])
        self.change_value.emit(self.progress)
        self.max_value.emit(self.total)
        if self.progress == self.total:
            self.change_value.emit(0)
            self.max_value.emit(0)


class Worker(QRunnable):

    def __init__(self, client, query_term, csv_name, metadata_fields, callback, auto_open):
        super().__init__()
        self.client = client
        self.query_term = query_term
        self.csv_name = csv_name
        self.metadata_fields = metadata_fields
        self.callback = callback
        self.auto_open = auto_open

    @Slot()  # QtCore.Slot
    def run(self):
        self.client.search_callback(self.callback)
        try:
            self.client.search_index_filter_csv(self.query_term, self.csv_name, self.metadata_fields)
        except:
            pass
        if self.auto_open:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', self.csv_name))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.csv_name)
            else:  # linux variants
                subprocess.call(('xdg-open', self.csv_name))


class ReportNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.report_name = ""
        self.setWindowTitle("Enter Report Name")

        self.report_label = QtWidgets.QLabel("Report File Name: ")
        self.report_text = QtWidgets.QLineEdit("")

        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)

        self.gridlayout.addWidget(self.report_label, 1, 1)
        self.gridlayout.addWidget(self.report_text, 1, 2)

        self.open_report = QtWidgets.QCheckBox("Open Report on Completion")
        self.open_report.setChecked(True)

        self.gridlayout.addWidget(self.open_report, 5, 2)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.gridlayout.addWidget(self.buttonBox, 6, 2)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def accept(self):
        name = self.report_text.text()
        if name.lower().endswith(".csv"):
            self.report_name = name
        else:
            self.report_name = name + ".csv"
        super().accept()

    def report(self):

        return self.report_name

    def auto_report(self):
        return self.open_report.isChecked()


class PasswordDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enter Preservica Credentials")
        self.resize(300, 200)
        self.setFixedSize(300, 200)

        self.username_label = QtWidgets.QLabel("Username: ")
        self.password_label = QtWidgets.QLabel("Password: ")
        self.tenant_label = QtWidgets.QLabel("Tenant: ")
        self.server_label = QtWidgets.QLabel("Server: ")

        self.username_text = QtWidgets.QLineEdit("")
        self.username_text.setToolTip("This is your username (email) for Preservica")
        self.password_text = QtWidgets.QLineEdit("")
        self.password_text.setToolTip("This is your password for Preservica")
        self.tenant_text = QtWidgets.QLineEdit("")
        self.tenant_text.setToolTip("This is short code for your tenancy name")
        self.server_text = QtWidgets.QLineEdit("")
        self.server_text.setToolTip("e.g eu.preservica.com or us.preservica.com etc")

        self.save_creds = QtWidgets.QCheckBox("Save Credentials")
        self.save_creds.setToolTip("Save your login details to a local file to auto-login on next run")

        self.gridlayout = QtWidgets.QGridLayout()
        self.setLayout(self.gridlayout)

        self.gridlayout.addWidget(self.username_label, 1, 1)
        self.gridlayout.addWidget(self.password_label, 2, 1)
        self.gridlayout.addWidget(self.tenant_label, 3, 1)
        self.gridlayout.addWidget(self.server_label, 4, 1)

        self.gridlayout.addWidget(self.username_text, 1, 2)
        self.gridlayout.addWidget(self.password_text, 2, 2)
        self.gridlayout.addWidget(self.tenant_text, 3, 2)
        self.gridlayout.addWidget(self.server_text, 4, 2)

        self.gridlayout.addWidget(self.save_creds, 5, 2)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.gridlayout.addWidget(self.buttonBox, 6, 2)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def username(self):
        return self.username_text.text()

    def password(self):
        return self.password_text.text()

    def tenant(self):
        return self.tenant_text.text()

    def server(self):
        return self.server_text.text()

    def accept(self):
        client = ContentAPI(username=self.username_text.text(),
                            password=self.password_text.text(),
                            tenant=self.tenant_text.text(),
                            server=self.server_text.text())

        if self.save_creds.isChecked():
            client.save_config()

        super().accept()


class ComboDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QComboBox in every
    cell of the column to which it's applied
    """

    def __init__(self, parent, index_name, model):
        QItemDelegate.__init__(self, parent)
        self.index_name = index_name
        self.model = model
        self.drop_down_row = -1

    def createEditor(self, parent, option, index):

        item_model = self.model
        index_name = item_model.item(index.row(), 0).text()

        if index_name == "xip.document_type":
            self.drop_down_row = index.row()
            combo = QComboBox(parent)
            li = list()
            li.append("Any")
            li.append("Asset")
            li.append("Folder")
            combo.addItems(li)
            self.connect(combo, SIGNAL("currentIndexChanged(int)"), self, SLOT("currentIndexChanged()"))
            return combo
        else:
            return QLineEdit(parent)

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        #editor.setCurrentIndex(int(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        if index.row() == self.drop_down_row:
            model.setData(index, editor.itemText(editor.currentIndex()))
        else:
            model.setData(index, editor.text())

    @Slot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


class MyWidget(QtWidgets.QWidget):

    @Slot()
    def run_report(self):
        dialog = ReportNameDialog()
        if dialog.exec_():
            metadata_fields = {}
            item_model = self.list.model()
            for i in range(item_model.rowCount()):
                qmodel_index = item_model.index(i, 0)
                index_name = item_model.item(i, 0).text()
                if item_model.itemData(qmodel_index).get(10) == 2:
                    metadata_fields[index_name] = ""
                    if hasattr(item_model.item(i, 1), "text"):
                        index_value = item_model.item(i, 1).text()
                        if index_name =="xip.document_type":
                            if index_value == "Asset":
                                index_value = "IO"
                            if index_value == "Folder":
                                index_value = "IO"
                            if index_value == "Any":
                                index_value = ""
                        metadata_fields[index_name] = index_value

            self.progress = QProgressDialog("Creating Report\n\nPlease Wait...", None, 0, 100)
            self.progress.setWindowTitle("Report")
            self.progress.setAutoClose(True)
            self.progress.setAutoReset(True)
            self.callback = CallBack()
            worker = Worker(self.client, self.search_value.text(), dialog.report(), metadata_fields, self.callback,
                            dialog.auto_report())
            self.callback.change_value.connect(self.progress.setValue)
            self.callback.max_value.connect(self.progress.setMaximum)
            self.threadpool.start(worker)
            self.progress.setModal(True)
            self.progress.show()

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.setWindowTitle("Preservica Solr Reporting")
        self.windowModality()
        self.progress = None
        self.callback = None

        self.search_label = QtWidgets.QLabel("Main Search Term (% returns everything)")
        self.search_value = QtWidgets.QLineEdit("%")

        self.help_label = QtWidgets.QLabel("Select from the list of indexed fields below to "
                                           "add columns to the output spreadsheet\n\n"
                                           "Indexes can have an optional filter term. Filters "
                                           "are only applied to selected fields")

        self.list = QTreeView()
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Index Name', 'Index Filter Term'])
        self.list.setModel(model)
        self.list.setUniformRowHeights(True)
        self.list.setAlternatingRowColors(True)
        self.list.setColumnWidth(0, 350)
        self.list.setColumnWidth(1, 250)

        self.list.setItemDelegateForColumn(1, ComboDelegate(self.list, "xip.document_type", model))

        if not os.path.isfile("credentials.properties"):
            dialog = PasswordDialog()
            if dialog.exec_():
                self.client = ContentAPI(dialog.username(), dialog.password(), dialog.tenant(), dialog.server())
            else:
                raise SystemExit
        else:
            self.client = ContentAPI()

        for index_name in self.client.indexed_fields():
            if index_name == "xip.full_text":
                continue
            index = QStandardItem(index_name)
            index.setCheckable(True)
            index.setEditable(False)

            if index_name == "xip.document_type":
                document_type = QComboBox()
                document_type.addItem("")
                document_type.addItem("IO")
                document_type.addItem("SO")
                filter_column = QStandardItem("")
            else:
                filter_column = QStandardItem("")
                filter_column.setEditable(True)

            model.appendRow([index])

        self.run_report_button = QtWidgets.QPushButton("Run Report")
        self.run_report_button.released.connect(self.run_report)

        self.list.setModel(model)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.search_label)
        self.layout.addWidget(self.search_value)
        self.layout.addWidget(self.help_label)
        self.layout.addWidget(self.list)
        self.layout.addWidget(self.run_report_button)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.setFixedSize(800, 600)
    widget.show()

    sys.exit(app.exec_())
