from BotCapabilities.ApiSfxReplicate import ApiSfxReplicate
from BotCapabilities.EkoInsightBot import EkoInsightBot
from BotCapabilities.LocalMask import LocalMask
from BotCapabilities.ApiImgDreamStudio import ApiImgDreamStudio
from BotCapabilities.ApiBlipReplicate import ApiBlipReplicate
from BotCapabilities.ApiChatGpt import ApiChatGpt
import os
import json


def load_config():
    CONFIG_ENV=os.getenv("CONFIG_ENV","qa-local")
    print(f"CONFIG_ENV {CONFIG_ENV} LOADED")
    return json.load(open(f"config/{CONFIG_ENV}/{CONFIG_ENV}.json"))

config_data=load_config()

img_identifier=ApiBlipReplicate(dry_run=True)
mask_provider=LocalMask(dry_run=False)
prompt_provider=ApiChatGpt(dry_run=True)
img_provider=ApiImgDreamStudio(dry_run=True)

sfx_provider=ApiSfxReplicate(dry_run=False)

ekoinsightbot=EkoInsightBot(prompt_provider,img_provider,img_identifier,mask_provider)

inpaint_path=ekoinsightbot.execute("kombucha_test.png")
