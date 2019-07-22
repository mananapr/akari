import sys
from akari.utils import loadDB
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QListWidgetItem, QListView, QHBoxLayout, QVBoxLayout

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('akari')
        self.setWindowIcon(QIcon('static/icon.png'))

        self.mainLayout = QHBoxLayout()

        self.sidePanel = QVBoxLayout()
        self.tagList = QListWidget()
        self.filerButton = QPushButton("Filter")
        self.sidePanel.addWidget(self.tagList)

        self.imagePanel = QVBoxLayout()
        self.imageList = QListWidget()
        self.imagePanelOptions = QHBoxLayout()
        self.miscButton1 = QPushButton("Misc Option 1")
        self.miscButton2 = QPushButton("Misc Option 2")
        self.imagePanel.addWidget(self.imageList)

        self.mainLayout.addLayout(self.sidePanel)
        self.mainLayout.addLayout(self.imagePanel)
        self.setLayout(self.mainLayout)

        self.initUI()

    def initUI(self):
        self.sidePanel.addWidget(self.filerButton, 1)

        self.imageList.setViewMode(QListView.IconMode) 
        self.imageList.setIconSize(QSize(300,300))

        self.imagePanel.addLayout(self.imagePanelOptions)
        self.imagePanelOptions.addWidget(self.miscButton1)
        self.imagePanelOptions.addWidget(self.miscButton2)

        self.show()

    def addImages(self, db):
        for imgPath in db:
            if imgPath == 'akari-tags':
                continue
            item = QListWidgetItem()
            icon = QIcon()
            pixmap = QPixmap(imgPath)
            icon.addPixmap(pixmap)
            item.setIcon(icon)
            self.imageList.addItem(item)

    def addTags(self, db):
        tagList = []
        for tag in sorted(db['akari-tags'], key=db['akari-tags'].get, reverse=True):
            tagList.append(str(db['akari-tags'][tag]) + ' ' + tag)
        self.tagList.addItems(tagList)

def init_gui():
    db = loadDB()
    app = QApplication(sys.argv)
    main = Main()
    main.addTags(db)
    main.addImages(db)
    sys.exit(app.exec_())
