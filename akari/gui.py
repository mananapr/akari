import sys
from akari.utils import loadDB, commit_changes
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QListWidgetItem, QListView, QHBoxLayout, QVBoxLayout, QAbstractItemView, QMenu, QInputDialog, QLineEdit, QMainWindow, QLabel, QDesktopWidget, QSplitter

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('akari')
        self.setWindowIcon(QIcon('static/icon.jpg'))
        self.db = None

        self.imageViewer = imageViewer()

        self.mainLayout = QHBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)
        self.leftSplitterWidget = QWidget()
        self.rightSplitterWidget = QWidget()
        self.splitter.addWidget(self.rightSplitterWidget)
        self.splitter.addWidget(self.leftSplitterWidget)

        self.sidePanel = QVBoxLayout()
        self.tagList = QListWidget()
        self.filerButton = QPushButton("Filter")
        self.clearFilerButton = QPushButton("Reset")
        self.sidePanel.addWidget(self.tagList)
        self.rightSplitterWidget.setLayout(self.sidePanel)

        self.imagePanel = QVBoxLayout()
        self.imageList = QListWidget()
        self.imagePanelOptions = QHBoxLayout()
        self.fsToggle = QPushButton("View Images in FullScreen")
        self.quitButton = QPushButton("Quit")
        self.imagePanel.addWidget(self.imageList)
        self.leftSplitterWidget.setLayout(self.imagePanel)

        self.mainLayout.addWidget(self.splitter)
        self.setLayout(self.mainLayout)

        self.initUI()

    def initUI(self):
        self.sidePanel.addWidget(self.filerButton, 1)
        self.sidePanel.addWidget(self.clearFilerButton, 1)
        self.tagList.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.imageList.setViewMode(QListView.IconMode)
        self.imageList.setIconSize(QSize(300,300))
        self.imageList.installEventFilter(self)

        self.imagePanel.addLayout(self.imagePanelOptions)
        self.imagePanelOptions.addWidget(self.fsToggle)
        self.imagePanelOptions.addWidget(self.quitButton)

        self.addEventHandlers()
        self.show()

    def updateDB(self, db):
        self.db = db

    def addEventHandlers(self):
        self.filerButton.clicked.connect(self.filterButton_pressed)
        self.clearFilerButton.clicked.connect(self.clearFilterButton_pressed)
        self.fsToggle.clicked.connect(self.fsToggle_pressed)
        self.quitButton.clicked.connect(self.close)

    def addTagEditingButtons(self):
        self.addTagsButton = QPushButton("Add New Tag")
        self.removeTagsButton = QPushButton("Remove Selected Tags")
        self.sidePanel.addWidget(self.addTagsButton)
        self.sidePanel.addWidget(self.removeTagsButton)
        self.addTagsButton.clicked.connect(self.addTagsButton_pressed)
        self.removeTagsButton.clicked.connect(self.removeTagsButton_pressed)

    def removeTagEditingButtons(self):
        try:
            self.sidePanel.removeWidget(self.addTagsButton)
            self.addTagsButton.deleteLater()
            self.sidePanel.removeWidget(self.removeTagsButton)
            self.removeTagsButton.deleteLater()
        except:
            pass

    def refreshTagListForImage(self, image):
        self.tagList.clear()
        for tag in self.db[image]:
            self.tagList.addItem(tag)

    def fsToggle_pressed(self):
        self.imageViewer.set_imageNumber(0)
        imageViewer_list = []
        for x in range(self.imageList.count()):
            imageViewer_list.append(self.imageList.item(x).data(0))
        self.imageViewer.set_imageViewerList(imageViewer_list)
        self.imageViewer.addImage(imageViewer_list[0])
        self.imageViewer.showFullScreen()

    def addTagsButton_pressed(self):
        image = self.imageList.item(0).data(0)
        tag, okPressed = QInputDialog.getText(self, "Enter Tag","Enter Tag", QLineEdit.Normal, "")
        if okPressed and tag != '':
            if tag not in self.db[image]:
                self.db[image].append(tag)
                if tag in self.db['akari-tags']:
                    self.db['akari-tags'][tag] = self.db['akari-tags'][tag] + 1
                else:
                    self.db['akari-tags'][tag] = 1
        commit_changes(self.db)
        self.db = loadDB()
        self.refreshTagListForImage(image)

    def removeTagsButton_pressed(self):
        tags_to_remove = self.tagList.selectedItems()
        image = self.imageList.item(0).data(0)
        for tag in tags_to_remove:
            tag = tag.text()
            self.db[image].remove(tag)
            self.db['akari-tags'][tag] = self.db['akari-tags'][tag] - 1
            if self.db['akari-tags'][tag] == 0:
                self.db['akari-tags'].pop(tag,None)
        commit_changes(self.db)
        self.db = loadDB()
        self.refreshTagListForImage(image)

    def filterButton_pressed(self):
        selected_items = self.tagList.selectedItems()
        selected_tags = []
        filtered_images = []
        for i in range(len(selected_items)):
            selected_tags.append(str(self.tagList.selectedItems()[i].text()).split(" ")[-1])
        for imgPath in self.db:
            if imgPath == 'akari-tags':
                continue
            if all(elem in self.db[imgPath] for elem in selected_tags):
                if imgPath not in filtered_images:
                    filtered_images.append(imgPath)
        self.addImages(filtered_images)
        self.removeTagEditingButtons()

    def clearFilterButton_pressed(self):
        imgList = self.getImgList()
        self.addImages(imgList)
        self.addTags()
        self.removeTagEditingButtons()

    def viewMetadata(self):
        selected_image = self.imageList.selectedItems()[0].data(0)
        tags = self.db[selected_image]
        self.tagList.clear()
        self.tagList.addItems(tags)
        self.addImages([selected_image])
        self.addTagEditingButtons()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if self.imageList.selectedItems() != []:
            viewMetadata = menu.addAction("View Metadata")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == viewMetadata:
                self.viewMetadata()

    def getImgList(self):
        imgList = []
        for imgPath in self.db:
            if imgPath == 'akari-tags':
                continue
            imgList.append(imgPath)
        return imgList

    def addImages(self, imgList):
        self.imageList.clear()
        for imgPath in imgList:
            item = QListWidgetItem()
            icon = QIcon()
            pixmap = QPixmap(imgPath)
            icon.addPixmap(pixmap)
            item.setFont(QFont("Times",1))
            item.setForeground(QColor("white"))
            item.setText(imgPath)
            item.setIcon(icon)
            self.imageList.addItem(item)

    def addTags(self):
        self.tagList.clear()
        tagList = []
        for tag in sorted(self.db['akari-tags'], key=self.db['akari-tags'].get, reverse=True):
            tagList.append(str(self.db['akari-tags'][tag]) + ' ' + tag)
        self.tagList.addItems(tagList)

class imageViewer(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.imageViewer_list = []
        self.imageNumber = None

    def set_imageViewerList(self, imgList):
        self.imageViewer_list = imgList

    def set_imageNumber(self, imageNumber):
        self.imageNumber = imageNumber

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right:
            try:
                self.addImage(self.imageViewer_list[self.imageNumber+1])
                self.imageNumber = self.imageNumber + 1
            except:
                self.imageNumber = 0
                self.addImage(self.imageViewer_list[self.imageNumber])
        elif key == Qt.Key_Left:
            try:
                self.addImage(self.imageViewer_list[self.imageNumber-1])
                self.imageNumber = self.imageNumber - 1
            except:
                self.imageNumber = len(self.imageViewer_list)-1
                self.addImage(self.imageViewer_list[self.imageNumber])
        elif key == Qt.Key_Q:
            self.hide()

    def addImage(self, image):
        pixmap = QPixmap(image)
        self.screenSize = QDesktopWidget().screenGeometry(0)
        self.setPixmap(pixmap.scaled(self.screenSize.width(), self.screenSize.height(), Qt.KeepAspectRatio))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color : black; }")

def init_gui():
    db = loadDB()
    app = QApplication(sys.argv)
    main = Main()
    main.updateDB(db)
    main.addTags()
    imgList = main.getImgList()
    main.addImages(imgList)
    sys.exit(app.exec_())
