

from BotCapabilities.BotClass import BotClass
from templates import *
import random
import json
from utils import *

class BotStory(BotClass):
    def __init__(self, config_data,story_provider, img_provider=None,sfx_provider=None,nber_pages=5):
        self.config=config_data
        self.story_provider = story_provider
        self.img_provider = img_provider
        self.sfx_provider = sfx_provider
        self.story_title=""
        self.nber_pages=nber_pages
        self.story_id=""
        self.stories_folder=self.config['stories_folder']
        self.assets_folder=self.config['assets_folder']
        check_create_folder(self.stories_folder)
        check_create_folder(self.assets_folder)

    def save_story(self,story_pages:dict):
        with open(f'{self.stories_folder}/{story_pages["title"][:200]}.json', 'w') as fp:
            json.dump(story_pages, fp)

    def fetch_story_plus_prompts(self,recyclable_item=False,story_setting=False,obstacle=False,temperature=0.9,nber_pages=5):
        #refine your fetching to return structured prompts as well
        #needs to work with chapters
        self.story_provider.recyclable_item=recyclable_item
        story=self.story_provider.fetch_story(recyclable_item,story_setting,obstacle,dry_run=False,nber_pages=self.nber_pages)
        pages_data=self.story_provider.fetch_img_prompts(story,nber_pages=nber_pages)
        return pages_data
        
    def fetch_complete_story(self,recyclable_item=random.choice(recyclable_items),story_setting=random.choice(story_settings),obstacle=random.choice(obstacles)):
        pages_data=self.fetch_story_plus_prompts(recyclable_item,story_setting,obstacle)
        self.story_title=pages_data['title']

        story_path=self.assets_folder+"/"+self.story_title.replace("'","").replace(" ","_").lower()
        check_create_folder(story_path)

        style=random.choice(DREAMSTUDIO_story_styles)
        for idx,page_data in enumerate(pages_data['story_pages']):
            page_path=story_path+"/"+str(idx)
            sfx_path=story_path+"/"+str(idx)+"/sfx"
            image_path=story_path+"/"+str(idx)+"/image"
            for folder_path in [page_path,sfx_path,image_path]:
                check_create_folder(folder_path) 
            full_img_path=self.fetch_img(page_data['image_prompt'],style=style,path=image_path)
            pages_data['story_pages'][idx]['img_file_path']=full_img_path

            """get sfx prompt"""
            sfx_prompt=self.story_provider.fetch_sfx_prompts(page_data['text'])
            if self.sfx_provider:
                print("fetching sfx")
                sfx_filename=sfx_prompt.replace(" ","_")+".wav"
                full_sfx_path=sfx_path+"/"+sfx_filename
                sfx_object=self.fetch_sfx_object(sfx_prompt)
                if sfx_object:
                    self.sfx_provider.save_sfx(sfx_object,full_sfx_path)
                pages_data['story_pages'][idx]['sfx_file_path']=full_sfx_path

        return pages_data

    def fetch_img(self,prompt,style=None,size="256x256",dry_run=False,path=""):
        if self.img_provider:
            prompt+=f" no humans ,no humans,no humans,beautiful, highly detailed"
            if style:
                prompt+=f", {style}"
            #negative prompt
            prompt+=f" | disfigured:-1.0, ugly:-1.0, humans:-1.0, text:-1.0"
            img=self.img_provider.fetch_img(prompt,path=path)
            return img
        return []

    def fetch_sfx_object(self,input_text):
        #returns SFX object
        sfx_object=None
        if self.sfx_provider:
            sfx_object=self.sfx_provider.fetch_sfx(input_text)
        return sfx_object

