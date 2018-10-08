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
        loadUi('src/InteractiveGUI3.ui',self)
        self.image = None
        self.cropped = None
        self.pushButton.clicked.connect(self.loadClicked)
        self.ProcessButton.clicked.connect(self.processImageClicked)        ## Loading of the model have to be done here.
        self.PolyButton.clicked.connect(self.getpolyClicked)

    #@pyqtSlot()
    def loadClicked(self):
        fname,filter = QFileDialog.getOpenFileName(self,'Open File','/home/uib06040/polyrnn',"Image Files (*.png)") ## Image browser
        if fname:
            self.readImage(fname)
        else:
            print('Invalid Image')
            #self.loadImage('dusseldorf_000002_000019_leftImg8bit.png')

    #@pyqtSlot()
    def getpolyClicked(self):
        self.cropped = cv2.imread("output/input.png")
        dim = (791,371)
        resized = cv2.resize(self.cropped, dim, interpolation = cv2.INTER_AREA)
        self.cropped = resized.copy()
        self.displayCroppedImage(window=2)

    #@pyqtSlot()
    def processImageClicked(self):     ## Image Cropping:: need to use self.cropped over here.
        cv2.imwrite("imgs/input.png", self.cropped)

        os.system("python src/inference.py \
            --PolyRNN_metagraph='../polyrnn/models/poly/polygonplusplus.ckpt.meta' \
            --PolyRNN_checkpoint='../polyrnn/models/poly/polygonplusplus.ckpt' \
            --EvalNet_checkpoint='../polyrnn/models/evalnet/evalnet.ckpt' \
            --InputFolder='imgs/' \
            --GGNN_checkpoint='../polyrnn/models/ggnn/ggnn.ckpt' \
            --GGNN_metagraph='../polyrnn/models/ggnn/ggnn.ckpt.meta' \
            --OutputFolder='output/' \
            --Use_ggnn=True")
        os.system("python src/vis_predictions.py \
                -pred_dir='output/' \
                --show_ggnn")

    def readImage(self,fname):
        self.image = cv2.imread(fname)
        #self.displayImage()

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
            cv2.rectangle(images, ref_point[0], ref_point[1], (0, 255, 0), 1) ## Last argument is the line width
            cv2.imshow("images", images)

        # image1 = cv2.imread(self.image)
        images = self.image # self.image = cv2.imread(fname)
        clone = images.copy()
        cv2.namedWindow("images")
        cv2.setMouseCallback("images", shape_selection)


        # keep looping until the 'q' key is pressed
        while True:
          # display the image and wait for a keypress
          cv2.imshow("images", images)
          key = cv2.waitKey(1) & 0xFF

          # if the 'r' key is pressed, reset the cropping region
          if key == ord("r"):
            images = clone.copy()

          # if the 'c' key is pressed, break from the loop
          elif key == ord("c"):
            break

        # if there are two reference points, then crop the region of interest
        # from the image and display it
        if len(ref_point) == 2:
            print("ref_point:", ref_point)
            crop_img = clone[ref_point[0][1]:ref_point[1][1], ref_point[0][0]:ref_point[1][0]]
            cv2.imshow("crop_img", crop_img)
            cv2.waitKey(0)
            self.cropped = crop_img.copy()
            print("Shape of the cropped Image:",self.cropped.shape)
            dim = (224,224)
            resized = cv2.resize(self.cropped, dim, interpolation = cv2.INTER_AREA)
            self.cropped = resized.copy()
            print("Shape of the resized Image:",self.cropped.shape)


        # close all open windows
        cv2.destroyAllWindows()
        self.displayCroppedImage()


    def displayCroppedImage(self, window =1):
        qformat = QImage.Format_Indexed8
        if len(self.cropped.shape) == 3: # rows[0],cols[1],channels[2]
            if(self.cropped.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(self.cropped, self.cropped.shape[1],self.cropped.shape[0],self.cropped.strides[0],qformat)

    #BGR > RGB

        img = img.rgbSwapped()
        if window == 1:
            self.imglabel.setPixmap(QPixmap.fromImage(img))
            self.imglabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        if window == 2:
            self.imglabel_2.setPixmap(QPixmap.fromImage(img))
            self.imglabel_2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

#if __name__ == '__main__':

app=QApplication(sys.argv)
window=InteractiveGUITest()
window.setWindowTitle('GUI for polyrnn++')
window.show()
sys.exit(app.exec_())
