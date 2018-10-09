import sys
import cv2
import os
import re

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog
from PyQt5.uic import loadUi

import matplotlib
matplotlib.use('Agg')

import tensorflow as tf
import glob
import numpy as np
from PolygonModel import PolygonModel
from EvalNet import EvalNet
from GGNNPolyModel import GGNNPolygonModel
import utils
import skimage.io as io
import tqdm
import json

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from poly_utils import vis_polys

ref_point = []
cropping = False

class InteractiveGUITest(QMainWindow):
    def __init__(self):
        super(InteractiveGUITest,self).__init__()
        loadUi('src/InteractiveGUI3.ui',self)

        self.image = None
        self.cropped = None
        self.pushButton.clicked.connect(self.loadClicked)
        self.ProcessButton.clicked.connect(self.processImageClicked)      ## Loading of the model have to be done here.
        self.PolyButton.clicked.connect(self.getpolyClicked)


    tf.logging.set_verbosity(tf.logging.INFO)
    # --
    global FLAGS
    flags = tf.flags
    FLAGS = flags.FLAGS
    # --- Some kind of placeholder for the input data like the checkpoints
    ## These FLAGS are useful as we need to change the folder structure only over here.

    flags.DEFINE_string('PolyRNN_metagraph', '', 'PolygonRNN++ MetaGraph ')
    flags.DEFINE_string('PolyRNN_checkpoint', '', 'PolygonRNN++ checkpoint ')
    flags.DEFINE_string('EvalNet_checkpoint', '', 'Evaluator checkpoint ')
    flags.DEFINE_string('GGNN_metagraph', '', 'GGNN poly MetaGraph ')
    flags.DEFINE_string('GGNN_checkpoint', '', 'GGNN poly checkpoint ')
    flags.DEFINE_string('InputFolder', '../imgs/', 'Folder with input image crops')
    flags.DEFINE_string('OutputFolder', '../output/', 'OutputFolder')
    flags.DEFINE_boolean('Use_ggnn', False, 'Use GGNN to postprocess output')

    #
    global _BATCH_SIZE, _FIRST_TOP_K, model, evalSess, polySess, ggnnSess, ggnnGraph, evalGraph, polyGraph, evaluator, ggnnModel
    _BATCH_SIZE = 1
    _FIRST_TOP_K = 5 ## Mainly for the first vertex predictions best of 5 is selected by the Evaluator

    evalGraph = tf.Graph()
    polyGraph = tf.Graph()

    # Evaluator Network
    tf.logging.info("Building EvalNet...")      ## Displaying INFO
    with evalGraph.as_default():                ## Making evalGraph as the default one in this scope
        with tf.variable_scope("discriminator_network"):
            evaluator = EvalNet(_BATCH_SIZE)
            evaluator.build_graph()
        saver = tf.train.Saver()

        # Start session
        evalSess = tf.Session(config=tf.ConfigProto(        ## loading the ckpt files here
            allow_soft_placement=True
        ), graph=evalGraph)
        saver.restore(evalSess, FLAGS.EvalNet_checkpoint)

    # PolygonRNN++
    tf.logging.info("Building PolygonRNN++ ...")
    model = PolygonModel(FLAGS.PolyRNN_metagraph, polyGraph)
    ## metagraph is something that reconstructs the structure of the network to restore the model.
    model.register_eval_fn(lambda input_: evaluator.do_test(evalSess, input_))

    polySess = tf.Session(config=tf.ConfigProto(
        allow_soft_placement=True
    ), graph=polyGraph)

    model.saver.restore(polySess, FLAGS.PolyRNN_checkpoint) ## N/W loaded to PolySess
    tf.logging.info("Poly is restored...")

    if FLAGS.Use_ggnn:
        ggnnGraph = tf.Graph()
        tf.logging.info("Building GGNN ...")
        ggnnModel = GGNNPolygonModel(FLAGS.GGNN_metagraph, ggnnGraph)
        ggnnSess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True
        ), graph=ggnnGraph)
        ggnnModel.saver.restore(ggnnSess, FLAGS.GGNN_checkpoint)

    tf.logging.info("GGNN is restored...")

    ### Testing the images on the model.
    def TestOnCrop(self):
            def save_to_json(crop_name, predictions_dict):
                    ## To save files to the json annotation about the poly vertices
                  output_dict = {'img_source': crop_name, 'polys': predictions_dict['polys'][0].tolist()}
                  if 'polys_ggnn' in predictions_dict:
                      output_dict['polys_ggnn'] = predictions_dict['polys_ggnn'][0].tolist()

                  fname = os.path.basename(crop_name).split('.')[0] + '.json'

                  fname = os.path.join(FLAGS.OutputFolder, fname)

                  json.dump(output_dict, open(fname, 'w'), indent=4)

            tf.logging.info("Testing...")
            if not os.path.isdir(FLAGS.OutputFolder):
                tf.gfile.MakeDirs(FLAGS.OutputFolder)
            crops_path = glob.glob(os.path.join(FLAGS.InputFolder, '*.png'))    ## generate a list of all the input input_images
            for crop_path in tqdm.tqdm(crops_path):
                image_np = io.imread(crop_path)             ## Input image read here
                image_np = np.expand_dims(image_np, axis=0) ## Image flattened to 1D
                preds = [model.do_test(polySess, image_np, top_k) for top_k in range(_FIRST_TOP_K)] ## model is PolygonModel

                ## sort predictions based on the eval score and pick the best
                preds = sorted(preds, key=lambda x: x['scores'][0], reverse=True)[0]

                if FLAGS.Use_ggnn:
                    polys = np.copy(preds['polys'][0])
                    feature_indexs, poly, mask = utils.preprocess_ggnn_input(polys)
                    preds_gnn = ggnnModel.do_test(ggnnSess, image_np, feature_indexs, poly, mask)
                    output = {'polys': preds['polys'], 'polys_ggnn': preds_gnn['polys_ggnn']}
                else:
                    output = {'polys': preds['polys']}

                # dumping to json files
                save_to_json(crop_path, output)

            show_ggnn = True
            preds_path = glob.glob(os.path.join(FLAGS.OutputFolder, '*.json'))
            fig, axes = plt.subplots(1, 2 if show_ggnn else 1, num=0,figsize=(12,6))
            axes = np.array(axes).flatten()
            for pred_path in tqdm.tqdm(preds_path):
                pred = json.load(open(pred_path, 'r'))
                file_name = pred_path.split('/')[-1].split('.')[0]

                im_crop, polys = io.imread(pred['img_source']), np.array(pred['polys'])  ## pred['polys'] contains the polygons
                vis_polys(axes[0], im_crop, polys, title='PolygonRNN++ : %s ' % file_name)
                if show_ggnn:
                    vis_polys(axes[1], im_crop, np.array(pred['polys_ggnn']), title=' PolygonRNN++ + GGNN : %s' % file_name)

                fig_name = os.path.join(FLAGS.OutputFolder, file_name) + '.png'
                fig.savefig(fig_name)

                [ax.cla() for ax in axes]

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
            self.TestOnCrop()

    def readImage(self,fname):
         self.image = cv2.imread(fname)
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

if __name__ == '__main__':
    app=QApplication(sys.argv)
    window=InteractiveGUITest()
    #tf.app.run()
    window.setWindowTitle('GUI for polyrnn++')
    window.show()
    sys.exit(app.exec_())
