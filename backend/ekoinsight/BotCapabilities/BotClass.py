import json
from ..utils import *


class BotClass():
    def __init__(self, dry_run=False):
        # LOAD ENV CONFIG
        self.config=load_config()
        self.dry_run = dry_run
        self.onnx_model_path = self.config["img_process"]["models"]["onnx"]
        self.checkpoint = self.config["img_process"]["models"]["checkpoint"]
        self.mask_output_dir = self.config["img_process"]["masks"]["output_paths"][
            "masks"
        ]
        self.except_mask_output_dir = self.config["img_process"]["masks"][
            "output_paths"
        ]["except_masks"]
        self.img_input_dir = self.config["img_process"]["masks"]["input_paths"]["imgs"]
        self.blurred_img_input_dir = self.config["img_process"]["masks"]["input_paths"]["blurred_imgs"]
        self.inpaint_output_dir = self.config["img_dreamstudio"]["output_paths"][
            "inpaint_save_path"
        ]
        self.generation_output_dir = self.config["img_dreamstudio"]["output_paths"][
            "generation_save_path"
        ]
        # making sure needed folders exist
        [
            check_create_folder(basic_dir)
            for basic_dir in [
                self.mask_output_dir,
                self.except_mask_output_dir,
                self.img_input_dir,
                self.blurred_img_input_dir,
                self.inpaint_output_dir,
                self.generation_output_dir,
            ]
        ]

        




    
    def set_engine(self, engine_type):
        # Available engines: stable-diffusion-xl-1024-v0-9 stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
        # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0

        self.engine = engine_type
        self.api = self.client.StabilityInference(
            key=self.key,
            verbose=True,  # Print debug messages.
            engine=self.engine,  # not sure why python puts it in a tuple...
        )
