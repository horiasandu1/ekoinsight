import os
import warnings
from PIL import Image
import io
from torchvision.transforms import GaussianBlur
from BotCapabilities.ApiDreamStudio import ApiDreamStudio
from BotCapabilities.BotClass import BotClass


class ApiImgDreamStudio(ApiDreamStudio):
    def __init__(self, dry_run=False):
        super().__init__(dry_run=dry_run)
        # https://dreamstudio.com/api/
        
        # Set the engine to use for generation.
        self.max_width = 512
        self.max_height = 512
        self.acceptable_ratios = {
            (21, 9),
            (16, 9),
            (3, 2),
            (5, 4),
            (1, 1),
            (4, 5),
            (2, 3),
            (9, 16),
            (9, 21),
        }


        #https://dreamstudio.com/api/
        from stability_sdk import client
        import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


        self.engine=self.config['ImgDreamStudio']['engines']['generation_engine']
        self.api=client.StabilityInference(
            key=self.api_key,
            verbose=True, # Print debug messages.
            engine=self.engine #not sure why python puts it in a tuple...
            )
        self.generation=generation



    def resize_image_64(self, img):


        width, height = img.size

        # Ensure dimensions are multiples of 64
        width -= width % 64
        height -= height % 64

        # Calculate new dimensions while maintaining proportions
        ratio = min(self.max_width / width, self.max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        # Calculate excess width and height
        excess_width = width - new_width
        excess_height = height - new_height

        # Cut off excess dimensions while preserving the middle
        left = excess_width // 2
        top = excess_height // 2
        right = width - (excess_width - left)
        bottom = height - (excess_height - top)

        # Crop the image to preserve the middle
        img = img.crop((left, top, right, bottom))

        # Find the closest acceptable ratio
        original_ratio = (new_width, new_height)

        if original_ratio not in self.acceptable_ratios:
            closest_ratio = min(self.acceptable_ratios, key=lambda ratio: abs((ratio[0] / ratio[1]) - (original_ratio[0] / original_ratio[1])))
            new_width = closest_ratio[0]*((original_ratio[0]+original_ratio[1])/(closest_ratio[0]+closest_ratio[1]))
            new_height = closest_ratio[1]*((original_ratio[0]+original_ratio[1])/(closest_ratio[0]+closest_ratio[1]))

        # Resize the image without stretching
        resized_img = img.resize((new_width, new_height), Image.BILINEAR)

        return resized_img

    def save_img(self, resps, prompt):
        for resp in resps:
            for artifact in resp.artifacts:
                if artifact.finish_reason == self.generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again."
                    )
                if artifact.type == self.generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(
                        self.path + f"{prompt.replace(' ','')[:30]}.png"
                    )  # Save our generated images with their seed number as the filename.
        print(f"saved inpainted img at {self.path}/{prompt.replace(' ','')[:30]}")
        return self.path + f"{prompt.replace(' ','')[:30]}.png"

    def fetch_img(self, prompt, width=512, height=512):
        
        self.path = self.config["ImgDreamStudio"]["output_paths"][
            "generation_save_path"
        ]

        if self.dry_run:
            return f"would have created a story with {self.provider_name} using prompt {prompt}"
        else:
            resps = self.api.generate(
                prompt=prompt, width=width, height=height, cfg_scale=9.0
            )

            return self.save_img(self, resps, prompt)

    def fetch_inpaint_img(
        self,
        img_filename,
        img_path=None,
        mask_path=None,
        mask_type="",  #'except' type, shows only the item, everything else is black
        prompt="mountains of trash on the beach, realistic, high definition, polluted",
    ):

        self.path = self.config["ImgDreamStudio"]["output_paths"]["inpaint_save_path"]


        if img_path:
            self.img_input_dir=img_path

        if not mask_path:
            if mask_type == "except":
                mask_path = self.except_mask_output_dir
            else:
                mask_path = self.mask_output_dir

        img_path = self.img_input_dir + img_filename


        img = Image.open(img_path)
        mask_i = Image.open(mask_path)

        img = self.resize_image_64(img)
        mask_i = self.resize_image_64(mask_i)

        width, height = img.size
        mask_i_width, mask_i_height = mask_i.size

        # would need to have a max img size

        img = img.resize((min(width, mask_i_width), min(height, mask_i_height)))
        mask_i = mask_i.resize((min(width, mask_i_width), min(height, mask_i_height)))

        blur = GaussianBlur(5, 20)
        mask = blur(mask_i)

        if self.dry_run:
            return f"would have created an inpaint img with with {self.provider_name}"
        else:
            resps = self.api.generate(
                prompt=prompt,
                init_image=img,
                mask_image=mask,
                start_schedule=1,
                # seed=1838510951,  # If attempting to transform an image that was previously generated with our API,
                # initial images benefit from having their own distinct seed rather than using the seed of the original image generation.
                steps=50,  # Amount of inference steps performed on image generation. Defaults to 30.
                # cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                # Setting this value higher increases the strength in which it tries to match your prompt.
                # Defaults to 7.0 if not specified.
                width=width,  # Generation width, if not included defaults to 512 or 1024 depending on the engine.
                height=height,  # Generation height, if not included defaults to 512 or 1024 depending on the engine.
                # sampler=generation.SAMPLER_K_DPMPP_2M, # Choose which sampler we want to denoise our generation with.
                sampler=self.generation.SAMPLER_K_DPMPP_2S_ANCESTRAL,  # Choose which sampler we want to denoise our generation with.
                # Defaults to k_lms if not specified. Clip Guidance only supports ancestral samplers.
                # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
                guidance_preset=self.generation.GUIDANCE_PRESET_FAST_BLUE,
            )

            return self.save_img(resps, prompt)
