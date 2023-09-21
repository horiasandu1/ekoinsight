from abc import ABC, abstractmethod
import os
from dotenv import load_dotenv 
from utils import load_config
class ApiClass(ABC):
    def __init__(self, API_NAME="API_NAME",dry_run=False):
        load_dotenv()
        self.api_key= os.getenv(f"{API_NAME}_API_KEY")
        self.provider_name = API_NAME
        self.config=load_config()
        self.dry_run=dry_run



    # @abstractmethod
    # def save_file(self, object_to_save, local_filename):
    #     pass

    # @abstractmethod
    # def api_fetch(self, input_text):
    #     pass