import replicate
import os
import requests
from BotCapabilities.ApiReplicate import ApiReplicate

class ApiSfxReplicate(ApiReplicate):
    def __init__(self,dry_run=False):
        super().__init__(dry_run=dry_run)
        pass

    def save_file(self,sfx_object, local_filename):
        with open(local_filename, 'wb') as f:
            f.write(sfx_object)

    def api_fetch(self,input_text,sfx_string="haoheliu/audio-ldm:b61392adecdd660326fc9cfc5398182437dbe5e97b5decfb36e1a36de68b5b95"):

        url = replicate.Client(api_token=self.REPLICATE_API_KEY).run(
            sfx_string,
            input={"text": input_text }
        )
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Downloaded {input_text} successfully")
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")
        return response.content