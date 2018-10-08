import sys
import cv2
import re

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi

class InteractiveGUITest(QMainWindow):
    def __init__(self):
        super(InteractiveGUITest,self).__init__()
        loadUi('InteractiveGUI1.ui',self)
        self.image = None
        self.pushButton.clicked.connect(self.loadClicked)
        self.ProcessButton.clicked.connect(self.saveClicked)

    @pyqtSlot()
    def loadClicked(self):
        fname,filter = QFileDialog.getOpenFileName(self,'Open File','/home/uib06040/polyrnn',"Image Files (*.png)")
        if fname:
            self.loadImage(fname)
        else:
            print('Invalid Image')
            #self.loadImage('dusseldorf_000002_000019_leftImg8bit.png')
    @pyqtSlot()
    def saveClicked(self):
        fname, filter = QFileDialog.getSaveFileName(self,'Save File','/home/uib06040/polyrnn',"Image Files (*.png)")
        print("name of the file:",fname) ## While saving need to include the extension to avoid the Error
        ## url = fname ## '/path/eds/vs/accescontrol.dat/d=12520/file1.dat'
        ## [x for x in url.split('/') if x[-4:] == '.png']

        ## print('Name of the filename:', x)
        if fname:
            cv2.imwrite(fname, self.image)
        else:
            print('Error')


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
        img = QImage(self.image, self.image.shape[1], self.image.shape[0], self.image.strides[0], qformat)

    #BGR > RGB

        img = img.rgbSwapped()
        self.imglabel.setPixmap(QPixmap.fromImage(img))
        self.imglabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

app=QApplication(sys.argv)
window=InteractiveGUITest()
window.setWindowTitle('GUI for polyrnn++')
window.show()
sys.exit(app.exec_())
