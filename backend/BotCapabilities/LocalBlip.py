import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import time
import pandas as pd
import os
import spacy
import re
from tqdm import tqdm


class LocalBlip():
    def __init__(self, blip_path="models/blip-image-captioning-large", device='cpu'):
        self.device=device
        self.processor=BlipProcessor.from_pretrained(blip_path)
        self.model=BlipProcessor.from_pretrained(blip_path).to(device)
        self.nlp=spacy.load("en_core_web_sm")

    def get_main_subject(self,sentence="The cat sat on the mat."):
        doc = self.nlp(sentence)
        subject = " ".join([token.text for token in doc if token.pos_ != "DET"])
        return subject.strip()

    def extract_colors(self,text):
        # Regular expression to match color names
        color_pattern = re.compile(r'\b(?:black|white|gray|red|blue|green|yellow|purple|brown|pink|orange|beige|turquoise|gold|silver|navy|maroon|teal|lavender|olive)\b', re.IGNORECASE)
        # Find all color mentions in the input text
        matches = color_pattern.findall(text)
        # If there are no matches, return None
        if len(matches) == 0:
            return None
        # Return the matched colors as a comma-separated string
        return [text,', '.join(matches)]

    def extract_info(self,raw_image,prompt = "a picture of",device="cuda"):

        if prompt:    
            #inputs = processor(raw_image, prompt, return_tensors="pt").to(device, torch.float16)
            inputs = self.processor(raw_image, prompt, return_tensors="pt").to(device)

            out = self.model.generate(**inputs)
            picture_of=self.processor.decode(out[0], skip_special_tokens=True)
            picture_of=picture_of.lower().replace(prompt.lower(),"")
        else:
            #inputs = processor(raw_image, return_tensors="pt").to(device, torch.float16)
            inputs = self.processor(raw_image, return_tensors="pt").to(device)
            out = self.model.generate(**inputs)
            picture_of=self.processor.decode(out[0], skip_special_tokens=True)
            picture_of=picture_of.lower()
        return picture_of


    def identify_img(self,file_path):

        raw_image = Image.open(os.path.join(file_path)).convert('RGB') 

        prompt="one of the things in the picture is "
        recyclable_item=self.extract_info(raw_image,prompt,device=self.device)
        recyclable_item_subject=self.get_main_subject(recyclable_item)

        #### colors ###
        prompt=f"color of {recyclable_item_subject} is "
        colors=self.extract_info(raw_image,prompt,device=self.device)
        colors=self.extract_colors(colors)

        if not colors:
            prompt=f"{recyclable_item_subject} is the color "
            colors=self.extract_info(raw_image,prompt,device=self.device)
            colors=self.extract_colors(colors)

        if colors:
            color_context=colors[0]
            colors=colors[1]
        else:
            color_context=None

        return dict(file_path=file_path,recyclable_item_subject=recyclable_item_subject,color_context=color_context,colors=colors)


    def identify_imgs_in_dir(self,img_dir="pics"):
        data=[]

        for file in tqdm(sorted(os.listdir(f"{img_dir}/"))):
            file_path=f"{img_dir}/file"
            img_info=self.identify_img(file_path)

            data.append([img_info])

        return data

