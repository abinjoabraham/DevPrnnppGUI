import os

def CropImage():
    os.system("python src/ImageCrop.py --image src/*.png")
    os.system("sleep 3s")
    os.system("cp crop_img_*.png imgs/")
    os.system("convert imgs/crop_img*.png -resize 224x224\! imgs/crop_image_1.png")
    os.system("mv imgs/crop_img*.png dmps/")
