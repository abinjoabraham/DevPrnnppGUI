import sys
import cv2
import os
import re

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi

ref_point = []
cropping = False


class InteractiveGUITest(QMainWindow):
    def __init__(self):
        super(InteractiveGUITest,self).__init__()
        loadUi('InteractiveGUI3.ui',self)
        self.image = None
        self.pushButton.clicked.connect(self.loadClicked)
        self.ProcessButton.clicked.connect(self.processImage)
        self.PolyButton.clicked.connect(self.operateonimageClicked)

    @pyqtSlot()
    def operateonimageClicked(self):
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) if len(self.image.shape)>=3 else self.image
        self.image = cv2.Canny(gray,100,200)
        self.displayImage(window=2)

    @pyqtSlot()
    def loadClicked(self):
        fname,filter = QFileDialog.getOpenFileName(self,'Open File','/home/uib06040/polyrnn',"Image Files (*.png)") ## Image browser
        if fname:
            self.loadImage(fname)
        else:
            print('Invalid Image')
            #self.loadImage('dusseldorf_000002_000019_leftImg8bit.png')
    @pyqtSlot()
    def processImage(self):     ## Image Cropping
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

        def shape_selection(event, x, y, flags, param):
          # grab references to the global variables
          global ref_point, cropping

          # if the left mouse button was clicked, record the starting
          # (x, y) coordinates and indicate that cropping is being
          # performed
          if event == cv2.EVENT_LBUTTONDOWN:
            ref_point = [(x, y)]
            cropping = True

          # check to see if the left mouse button was released
          elif event == cv2.EVENT_LBUTTONUP:
            # record the ending (x, y) coordinates and indicate that
            # the cropping operation is finished
            ref_point.append((x, y))
            cropping = False

            # draw a rectangle around the region of interest
            cv2.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 1) ## Last argument is the line width
            cv2.imshow("image", image)

        # image1 = cv2.imread(self.image)
        clone = self.image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", shape_selection)


        # keep looping until the 'q' key is pressed
        while True:
          # display the image and wait for a keypress
          cv2.imshow("image", image)
          key = cv2.waitKey(1) & 0xFF

          # if the 'r' key is pressed, reset the cropping region
          if key == ord("r"):
            image = clone.copy()

          # if the 'c' key is pressed, break from the loop
          elif key == ord("c"):
            break

        # if there are two reference points, then crop the region of interest
        # from the image and display it
        if len(ref_point) == 2:
          crop_img = clone[ref_point[0][1]:ref_point[1][1], ref_point[0][0]:ref_point[1][0]]
          cv2.imshow("crop_img", crop_img)
          cv2.waitKey(0)

        # close all open windows
        cv2.destroyAllWindows()


    def displayImage(self, window=1):
        qformat = QImage.Format_Indexed8

        if len(self.image.shape) == 3: # rows[0],cols[1],channels[2]
            if(self.image.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(self.image, self.image.shape[1],self.image.shape[0],self.image.strides[0],qformat)

    #BGR > RGB

        img = img.rgbSwapped()
        if window == 1:
            self.imglabel.setPixmap(QPixmap.fromImage(img))
            self.imglabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        if window == 2:
            self.imglabel2.setPixmap(QPixmap.fromImage(img))
            self.imglabel2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

app=QApplication(sys.argv)
window=InteractiveGUITest()
window.setWindowTitle('GUI for polyrnn++')
window.show()
sys.exit(app.exec_())
