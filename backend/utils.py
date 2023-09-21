
import cv2
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
import onnxruntime
from tqdm import tqdm
import os
import re
import json

def load_config():
    CONFIG_ENV=os.getenv("CONFIG_ENV","qa-local")
    return json.load(open(f"config/{CONFIG_ENV}/{CONFIG_ENV}.json"))


def check_create_folder(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        print("created folder : ", dir)


def resize_img(image,square=False,square_dim=512):

    width=image.shape[1]
    height=image.shape[0]

    height_max=None
    width_max=None


    if width>height:
        width_max=square_dim

    elif height>width:
        height_max=square_dim

    else: #dealing with a square
        width_max=square_dim
        height_max=square_dim
    if width_max:
        pct_fraction=int(min(width,width_max))/width
    else:
        pct_fraction=int(min(height,height_max))/height

    width = int(width * pct_fraction)
    height = int(height * pct_fraction)
    dim = (width, height)

    # resize image
    image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

    if square:
        mid_h = int(height/2)
        mid_w = int(width/2)
        start_h = mid_h - min(mid_h,256)
        end_h = mid_h + min(mid_h,256)
        start_w = mid_w - min(mid_w,256)
        end_w = mid_w + min(mid_w,256)

        # extract the middle 256x256 square
        image = image[start_h:end_h, start_w:end_w]

    return image


