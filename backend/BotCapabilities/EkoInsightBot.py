

from BotCapabilities.BotClass import BotClass
from templates import *
from utils import *
import time
from dotenv import load_dotenv

class EkoInsightBot(BotClass):
    def __init__(self,prompt_provider, img_provider,img_identifier,mask_provider,identified_object=None,sfx_provider=None):
        super().__init__()
        self.prompt_provider = prompt_provider
        self.img_provider = img_provider
        self.img_identifier = img_identifier
        self.mask_provider = mask_provider
        self.sfx_provider = sfx_provider
        self.img_filename=""
        self.img_input_dir=self.config['input_paths']['imgs']
        self.identified_object=identified_object

    def execute(self,img_filename,img_path=None):
        self.img_filename=img_filename
        if img_path:
            if not img_path.endswith("/"):
                img_path+="/"
            self.img_input_dir=img_path
        self.img_full_path=self.img_input_dir+self.img_filename

        ###IMG GENERATION PART
        if not self.identified_object:
            start=time.time()
            self.identified_object=self.img_identifier.execute(img_path=self.img_full_path) 
            print(f"img identified : {self.identified_object} : took {time.time()-start}s") #takes about 3 seconds

        start=time.time()
        mask_path=self.mask_provider.execute(img_path=self.img_full_path)
        print(f"mask path provided : {mask_path} : took {time.time()-start}s")#takes about 33 seconds!

        start=time.time()
        pollution_prompt=self.prompt_provider.fetch_prompt(item=self.identified_object,prompt_template='pollution_prompt_template')
        pollution_prompt+=" realistic, high definition, polluted"
        print(f"pollution_prompt generated : took {time.time()-start}s")
        print(f"pollution_prompt : {pollution_prompt}")

        start=time.time()
        inpaint_img_path=self.img_provider.fetch_inpaint_img(img_filename=img_filename,img_path=self.img_input_dir,mask_path=mask_path,prompt=pollution_prompt)
        print(f"inpaint_img_path produced : took {time.time()-start}s")
        print(f"inpaint_img_path : {inpaint_img_path}")


        #return this in a format that's useful
        #get the stats query ready.


        ####EDUCATION PART
        #general education
        start=time.time()
        education_info=self.prompt_provider.fetch_prompt(item=self.identified_object,prompt_template='educate_prompt_template',max_new_tokens=500, stop_sequences= ["END"])
        print(f"education_info generated : took {time.time()-start}s")
        print(f"education_info : {education_info}") 
        education_info=eval(education_info.split("= ")[1])


        #from the vector database pinecone
        vectorsearch_info=None
        start=time.time()
        #try:
        query=f"give me interesting facts related to {education_info['likely_material_and_item']}"
        vectorsearch_info=self.prompt_provider.fetch_using_index(query=query)
            
            
        # except Exception as e:
        #     print(e)
        #     print("failed in fetching vectorsearch_info")
        print(f"vectorsearch_info query : took {time.time()-start}s")
        print(f"vectorsearch_info : {vectorsearch_info}")



        return {"inpaint_img_path":inpaint_img_path,"education_info":education_info,"vectorsearch_info":vectorsearch_info}

    def identify_img(self):
        self.img_identifier.identify_img(self.img_path)


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
