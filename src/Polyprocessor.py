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


preds_path = glob.glob(os.path.join(FLAGS.OutputFolder, '*.json'))
for pred_path in tqdm.tqdm(preds_path):
    pred = json.load(open(pred_path, 'r'))
    file_name = pred_path.split('/')[-1].split('.')[0]
    im_crop = cv2.imread(pred['img_source'])
    polys = np.array(pred['polys'])
    pix = np.multiply(polys,100)
    pix = np.around(pix,decimals=0)
    #pix = np.expand_dims(pix, axis=0)
    #print('Polys Expand::',pix)
    pix = pix.reshape((-1, 1, 2))
    print('Polys::',pix)
    dim = (224,224)
    resized = cv2.resize(im_crop, dim, interpolation = cv2.INTER_AREA)
    print('size of image:',resized.shape)
    cv2.imshow("test",im_crop)
    #polyspix = np.array(pred['polys']*100,np.uint8)
    cv2.polylines(im_crop,[np.int32(pix)],True,(0,0,255))       ## Outer [] was important for closed poly
    #cv2.fillPoly(im_crop,[np.array(pix, dtype=np.int32)], (0,0,255))
    winname = 'example'
    cv2.namedWindow(winname)
    cv2.imshow(winname, im_crop)
    cv2.waitKey()
    cv2.destroyAllWindows()
