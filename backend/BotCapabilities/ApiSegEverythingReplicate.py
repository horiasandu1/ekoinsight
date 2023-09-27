import replicate
import os
from BotCapabilities.ApiReplicate import ApiReplicate
import spacy
import cv2
import numpy as np
import requests
from utils import *
class ApiSegEverythingReplicate(ApiReplicate):
    #https://replicate.com/yyjim/segment-anything-tryout
    def __init__(self,dry_run=False):
        super().__init__(dry_run=dry_run)
        #python -m spacy download en_core_web_sm
        self.nlp=spacy.load("en_core_web_sm")
        self.dry_run=dry_run
        self.img_path=""
        self.blurred_img_dir=self.config["ImgProcess"]["masks"]["input_paths"]["blurred_imgs"]
        self.mask_dir=self.config['ImgProcess']['masks']['output_paths']['masks']
        self.except_mask_dir=self.config['ImgProcess']['masks']['output_paths']['except_masks']
        check_create_folder(self.mask_dir)
        check_create_folder(self.except_mask_dir)
        check_create_folder(self.blurred_img_dir)



    def save_file(self,file_object, local_filename):
        with open(local_filename, 'wb') as f:
            f.write(file_object)


    def get_blurred_img(self):
        #BLURRING
        image = cv2.imread(self.img_path)
        image = self.resize_img(image, square=True)
        ksize = (7, 7)
        blurred_image = cv2.blur(image, ksize)
        self.image_name=self.img_path.split("/")[-1]
        self.blurred_img_path=self.blurred_img_dir+"blurred_"+self.img_path.split("/")[-1]

        height, width, _ = blurred_image.shape

        # Create a mask with a clear center circle and blurred outer area
        mask = np.zeros((height, width), dtype=np.uint8)
        center = (width // 2, height // 2)
        radius = min(width, height) * 5 // 8  # Adjust the radius to control the clear area size
        cv2.circle(mask, center, radius, 255, -1)  # 255 is the value for white

        # Apply Gaussian blur to the image outside the clear circle
        circular_blurred_image = cv2.GaussianBlur(blurred_image, (0, 0), sigmaX=10)  # Adjust sigmaX to control blur intensity

        # Combine the original image and the blurred image using the mask
        result = cv2.bitwise_and(blurred_image, blurred_image, mask=mask)
        result += cv2.bitwise_and(circular_blurred_image, blurred_image, mask=cv2.bitwise_not(mask))
        blurred_image=result
        cv2.imwrite(self.blurred_img_path, blurred_image)

    
    def api_fetch(self,sfx_string="yyjim/segment-anything-everything:b28e02c3844df2c44dcb2cb96ba2496435681bf88878e3bd0ab6b401a971d79e"):

        #bounding_box=self.get_bounding_box()
        self.get_blurred_img()
        
        if not self.dry_run:
            image_url = replicate.Client(api_token=self.api_key).run(
                sfx_string,
                input={"image": open(self.blurred_img_path, "rb"),
                    "mask_limit":1,
                    'mask_only':True,
                    }
            )
            image_url=image_url[0]
            assert "http" in image_url
            # Send an HTTP GET request to the URL
            response = requests.get(image_url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Read the image data from the response content
                image_data = np.frombuffer(response.content, dtype=np.uint8)

                # Decode the image using OpenCV
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                # Save the image locally
                if image is not None:
                    full_mask_path=f"{self.mask_dir}{self.image_name}"
                    cv2.imwrite(full_mask_path, image)
                    
                    print(f"MASK saved :{full_mask_path}")
                    return f"{full_mask_path}"
                else:
                    print('Failed to decode  MASK.')

            else:
                print('Failed to fetch the MASK from the URL. Status code:', response.status_code)
            return None
        else:

            return f"{self.mask_dir}kombucha_test.png"
    
    def execute(self,img_path):
        self.img_path=img_path
        return self.api_fetch()