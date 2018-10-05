import sys
import cv2

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow
from PyQt5.uic import loadUi

class InteractiveGUITest(QMainWindow):
    def __init__(self):
        super(InteractiveGUITest,self).__init__()
        loadUi('InteractiveGUI.ui',self)
        self.image = None
        self.pushButton.clicked.connect(self.loadClicked)

    @pyqtSlot()
    def loadClicked(self):
        self.loadImage('dusseldorf_000002_000019_leftImg8bit.png')

    def loadImage(self,fname):
        self.image = cv2.imread(fname)
        self.displayImage()

    def displayImage(self):
        qformat = QImage.Format_Indexed8

        if len(self.image.shape) == 3: # rows[0],cols[1],channels[2]
            if(self.image.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(self.image, self.image.shape[1],self.image.shape[0],self.image.strides[0],qformat)

    #BGR > RGB

        img = img.rgbSwapped()
        self.imglabel.setPixmap(QPixmap.fromImage(img))
        self.imglabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

app=QApplication(sys.argv)
window=InteractiveGUITest()
window.setWindowTitle('GUI for polyrnn++')
window.show()
sys.exit(app.exec_())
