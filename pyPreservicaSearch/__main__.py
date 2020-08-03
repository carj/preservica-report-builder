import sys
from PySide2.QtWidgets import QApplication
from pyPreservicaSearch.pyPreservicaSearch import MyWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MyWidget()
    widget.resize(800, 600)
    widget.setFixedSize(800, 600)
    widget.show()

    sys.exit(app.exec_())
