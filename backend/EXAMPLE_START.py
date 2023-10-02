from BotCapabilities.ApiSfxReplicate import ApiSfxReplicate
from BotCapabilities.EkoInsightBot import EkoInsightBot
from BotCapabilities.LocalMask import LocalMask
from BotCapabilities.ApiImgDreamStudio import ApiImgDreamStudio
from BotCapabilities.ApiBlipReplicate import ApiBlipReplicate
from BotCapabilities.ApiChatGpt import ApiChatGpt
from BotCapabilities.ApiSegEverythingReplicate import ApiSegEverythingReplicate
from BotCapabilities.ApiWatsonX import ApiWatsonX
import os
import json


def load_config():
    CONFIG_ENV=os.getenv("CONFIG_ENV","qa-local")
    print(f"CONFIG_ENV {CONFIG_ENV} LOADED")
    return json.load(open(f"config/{CONFIG_ENV}/{CONFIG_ENV}.json"))

config_data=load_config()

img_identifier=ApiBlipReplicate(dry_run=False)
#mask_provider=LocalMask(dry_run=False)
mask_provider=ApiSegEverythingReplicate(dry_run=False)
prompt_provider=ApiChatGpt(dry_run=False)
#prompt_provider=ApiWatsonX(dry_run=False)
img_provider=ApiImgDreamStudio(dry_run=False)

sfx_provider=ApiSfxReplicate(dry_run=False)

ekoinsightbot=EkoInsightBot(prompt_provider,img_provider,img_identifier,mask_provider)

data=ekoinsightbot.execute("kombucha_test.png")

"""
data will look like this

{"inpaint_img_path":inpaint_img_path,"education_info":education_info,"vectorsearch_info":vectorsearch_info}
"""

print("got here")