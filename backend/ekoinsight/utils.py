
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
from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.document_loaders.xml import UnstructuredXMLLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import TextLoader

loaders_dict = {
    '.pdf': PyMuPDFLoader,
    '.xml': UnstructuredXMLLoader,
    '.csv': CSVLoader,
    '.txt':TextLoader
}

def load_config():
    CONFIG_ENV=os.getenv("CONFIG_ENV","qa-local")
    return json.load(open(f"config/{CONFIG_ENV}/{CONFIG_ENV}.json"))


def check_create_folder(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        print("created folder : ", dir)


def absolute_file_paths(directory):
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))

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



def document_file_paths(directory):
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            yield f



def load_docs(directory):
    # Create an instance of the DirectoryLoader with the provided directory path.
    loader = DirectoryLoader(directory,use_multithreading=True)
    # Use the loader to load the documents from the directory and store them in 'documents'.
    documents = loader.load()
    # Return the loaded documents.
    return documents

def create_directory_loader(file_type, directory_path):
    return DirectoryLoader(
        path=directory_path,
        glob=f"**/*{file_type}",
        loader_cls=loaders_dict[file_type],
        loader_kwargs={"encoding":'utf8'}
    )

def get_loaders(dir="recycling_data_dir"):
  extensions=loaders_dict.keys()
  return [create_directory_loader(extension,dir) for extension in extensions]

# Function to find the first URL in a given text
def find_first_url(text):
    url_pattern = r'https?://\S+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None