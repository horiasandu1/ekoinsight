from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv 
from utils import load_config
from langchain.vectorstores import Pinecone
import pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from utils import *
from langchain.document_loaders.merge import MergedDataLoader
from langchain.text_splitter import CharacterTextSplitter
import time
import cv2
class ApiClass(ABC):
    def __init__(self, API_NAME="API_NAME",dry_run=False):
        load_dotenv()
        self.api_key= os.getenv(f"{API_NAME}_API_KEY")
        self.provider_name = API_NAME
        self.config=load_config()
        self.dry_run=dry_run

    def produce_index_pinecone(self,index_name='cfc',docs_dir="recycling_data_dir",embeddings=None):
        load_dotenv()
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

        if not embeddings:
            model_id = 'sentence-transformers/all-MiniLM-L6-v2'
            model_kwargs = {'device': 'cpu'}
            embeddings = HuggingFaceEmbeddings(
                model_name=model_id,
                model_kwargs=model_kwargs
            )

        if PINECONE_API_KEY:
            environment="us-west4-gcp-free"

            pinecone.init(api_key=PINECONE_API_KEY, environment=environment)

            if index_name not in pinecone.list_indexes():
                pinecone.create_index(name=index_name, dimension=384, metric="cosine")
            
                loaders_list=get_loaders(docs_dir)
                loader_all = MergedDataLoader(loaders=loaders_list)
                docs=loader_all.load()

                for idx,page in enumerate(docs):
                    file_path=page.metadata['source']
                    if file_path.endswith(".txt"):
                        with open(file_path, 'r', encoding='utf-8') as file:
                            text = file.read()
                            first_url = find_first_url(text)
                            if first_url:
                                docs[idx].metadata['source']=first_url

                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                docs = text_splitter.split_documents(docs)
                time.sleep(5)
                index = Pinecone.from_documents(documents=docs, embedding=embeddings, index_name=index_name)

            else:
                # if you already have an index, you can load it like this
                index = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
                time.sleep(5)
            self.index=index
        else:
            print("NO PINECONE_API_KEY DETECTED!!!")


    def resize_img(self,image, square=False, square_dim=512):
        width = image.shape[1]
        height = image.shape[0]

        height_max = None
        width_max = None

        if width > height:
            width_max = square_dim

        elif height > width:
            height_max = square_dim

        else:  # dealing with a square
            width_max = square_dim
            height_max = square_dim
        if width_max:
            pct_fraction = int(min(width, width_max)) / width
        else:
            pct_fraction = int(min(height, height_max)) / height

        width = int(width * pct_fraction)
        height = int(height * pct_fraction)
        dim = (width, height)

        # resize image
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

        if square:
            mid_h = int(height / 2)
            mid_w = int(width / 2)
            start_h = mid_h - min(mid_h, 256)
            end_h = mid_h + min(mid_h, 256)
            start_w = mid_w - min(mid_w, 256)
            end_w = mid_w + min(mid_w, 256)

            # extract the middle 256x256 square
            image = image[start_h:end_h, start_w:end_w]

        return image
    
    # @abstractmethod
    # def save_file(self, object_to_save, local_filename):
    #     pass

    # @abstractmethod
    # def api_fetch(self, input_text):
    #     pass