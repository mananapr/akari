import sys
from PyQt5.QtWidgets import QApplication, QWidget

def init_gui():
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('akari')
    w.show()
    sys.exit(app.exec_())
