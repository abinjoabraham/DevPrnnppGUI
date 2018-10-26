import glob
import json
import os
import skimage.io as io
import tensorflow as tf
import cv2
import tqdm
import numpy as np

flags = tf.flags
FLAGS = flags.FLAGS

flags.DEFINE_string('OutputFolder', '../output/', 'OutputFolder')
image = cv2.imread('output/input.png')
cv2.imshow("test image", image)
imgcrop = image[72:534 , 77:539]
cv2.imshow("test image", imgcrop)
cv2.waitKey(0)
