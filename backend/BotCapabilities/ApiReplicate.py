import os
from BotCapabilities.ApiClass import ApiClass


class ApiReplicate(ApiClass):
    def __init__(self,API_NAME="REPLICATE",dry_run=False):
        super().__init__(API_NAME,dry_run)

    # def save_file(self,object_to_save, local_filename):
    #     pass

    # def api_fetch(self,input_text):
    #     pass