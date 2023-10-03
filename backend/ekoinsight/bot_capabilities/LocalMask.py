import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from .BotClass import BotClass
import utils


class LocalMask(BotClass):
    def __init__(self,dry_run=False, device="cpu"):

        super().__init__(dry_run)

        self.mask_dir=self.config['img_process']['masks']['output_paths']['masks']
        self.except_mask_dir=self.config['img_process']['masks']['output_paths']['except_masks']
        utils.check_create_folder(self.mask_dir)
        utils.check_create_folder(self.except_mask_dir)

        self.device = device
        model_type = "default"

        sam = utils.sam_model_registry[model_type](checkpoint=self.checkpoint)
        # can run this with cpu if you wanted
        sam.to(device=self.device)
        self.predictor = utils.SamPredictor(sam)
        self.ort_session = utils.onnxruntime.InferenceSession(self.onnx_model_path)#providers='CPUExecutionProvider'

    def produce_mask(self):
        # img_filename=img_path.split("/")[-1]
        # img_path=f'{img_path}{img_filename}'
        self.image_name=self.img_path.split("/")[-1]
        image = cv2.imread(self.img_path)
        #image = self.resize_img(image, square=True)

        ###BLURRING IMAGE
        ksize = (7, 7)
        blurred_image = cv2.blur(image, ksize)

        # blurred_image=image

        self.predictor.set_image(blurred_image)
        image_embedding = self.predictor.get_image_embedding().cpu().numpy()

        x = image.shape[1]
        y = image.shape[0]

        input_point = np.array([[int(x / 2), int(y / 2)]])
        input_label = np.array([1])  # 1 means that point is on what you want to detect

        # with input box
        input_box_coords = np.array(
            [int(x * 0.1), int(y * 0.5), int(x * 0.75), int(y * 0.25)]
        )
        input_box = input_box_coords.reshape(2, 2)
        box_label = np.array([2, 3])

        # without input box
        input_box = np.array([[0.0, 0.0]])
        box_label = np.array([-1])

        onnx_coord = np.concatenate([input_point, input_box], axis=0)[None, :, :]
        onnx_label = np.concatenate([input_label, box_label], axis=0)[None, :].astype(
            np.float32
        )

        onnx_coord = self.predictor.transform.apply_coords(
            onnx_coord, image.shape[:2]
        ).astype(np.float32)

        onnx_mask_input = np.zeros((1, 1, 256, 256), dtype=np.float32)
        # onnx_mask_input = np.zeros((1, 1, *image.shape[:2]), dtype=np.float32)
        onnx_has_mask_input = np.zeros(1, dtype=np.float32)

        ort_inputs = {
            "image_embeddings": image_embedding,
            "point_coords": onnx_coord,
            "point_labels": onnx_label,
            "mask_input": onnx_mask_input,
            "has_mask_input": onnx_has_mask_input,
            "orig_im_size": np.array(image.shape[:2], dtype=np.float32),
        }

        masks, _, low_res_logits = self.ort_session.run(None, ort_inputs)
        # print(predictor.model.mask_threshold)
        masks = masks > self.predictor.model.mask_threshold

        print(f"saving mask to {self.mask_output_dir}/{self.image_name}")
        self.save_mask(
            masks[0][-1],
            self.mask_output_dir,
            color="white",
            figsize=(10, 10),
            img_filename=self.image_name,
        )
        return f"{self.mask_output_dir}{self.image_name}"

    # def mask_producer_dir(self):
    #     for img_filename in tqdm(sorted(os.listdir(self.img_input_dir))):
    #         if img_filename.endswith("jpg") or img_filename.endswith("png"):
    #             self.produce_mask(img_filename=img_filename,img_path=f"{self.img_input_dir}/{img_filename}")

    def produce_except_mask(self, img_filename):
        mask = cv2.imread(
            f"{self.mask_output_dir}/{img_filename}", cv2.IMREAD_GRAYSCALE
        )
        # mask = cv2.bitwise_not(mask)
        # masks were already squares, gonna make this more elegant later on
        image = cv2.imread(f"{self.img_input_dir}/{img_filename}")
        image = self.resize_img(image, square=True)

        # Resize the images to the same size
        if mask.shape != image.shape[:2]:
            if mask.shape < image.shape[:2]:
                mask = cv2.resize(
                    mask, image.shape[:2][::-1], interpolation=cv2.INTER_AREA
                )
            else:
                image = cv2.resize(
                    image, mask.shape[::-1], interpolation=cv2.INTER_AREA
                )

        # Apply the inverted mask to the original image using bitwise_and operation

        # if mask.shape != image.shape[:2]:
        #     mask = cv2.resize(mask, image.shape[:2][::-1], interpolation=cv2.INTER_AREA)

        masked_img = cv2.bitwise_and(image, image, mask=mask)

        # Save the masked image
        cv2.imwrite(f"{self.except_mask_output_dir}/{img_filename}", masked_img)

    # def except_mask_producer_dir(self):
    #     for img_filename in tqdm(sorted(os.listdir(self.img_input_dir))):
    #         if img_filename.endswith("jpg") or img_filename.endswith("png"):
    #             self.produce_except_mask(img_filename)

    def resize_img(self,image, square=False, square_dim=512):
        width = image.shape[1]
        height = image.shape[0]

        height_max = None
        width_max = None

        if width > height:
            width_max = square_dim

        elif height > width:
            height_max = square_dim

        else:  # dealing with a square
            width_max = square_dim
            height_max = square_dim
        if width_max:
            pct_fraction = int(min(width, width_max)) / width
        else:
            pct_fraction = int(min(height, height_max)) / height

        width = int(width * pct_fraction)
        height = int(height * pct_fraction)
        dim = (width, height)

        # resize image
        image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

        if square:
            mid_h = int(height / 2)
            mid_w = int(width / 2)
            start_h = mid_h - min(mid_h, 256)
            end_h = mid_h + min(mid_h, 256)
            start_w = mid_w - min(mid_w, 256)
            end_w = mid_w + min(mid_w, 256)

            # extract the middle 256x256 square
            image = image[start_h:end_h, start_w:end_w]

        return image

    def save_mask(self,
        mask, mask_dir, color="white", figsize=(10, 10), img_filename="img.jpg"
    ):
        
        check_create_folder(mask_dir)

        if color == "random":
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)

        elif color == "blue":
            color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
        else:
            # white for mask extraction
            color = np.array([0 / 255, 0 / 255, 0 / 255, 1])

        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1)  # * color.reshape(1, 1, -1)

        # base_mask = np.zeros((h, w), dtype=np.uint8) * 255

        arr_scaled = (mask_image * 255).astype(np.uint8)

        # arr_scaled = cv2.bitwise_not(arr_scaled)

        cv2.imwrite(f"{mask_dir}/{img_filename}", arr_scaled)

    def show_masks(self,mask, ax, random_color=False):
        if random_color:
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        else:
            color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
        ax.imshow(mask_image)

    def show_points(self,coords, labels, ax, marker_size=375):
        pos_points = coords[labels == 1]
        neg_points = coords[labels == 0]
        ax.scatter(
            pos_points[:, 0],
            pos_points[:, 1],
            color="green",
            marker="*",
            s=marker_size,
            edgecolor="white",
            linewidth=1.25,
        )
        ax.scatter(
            neg_points[:, 0],
            neg_points[:, 1],
            color="red",
            marker="*",
            s=marker_size,
            edgecolor="white",
            linewidth=1.25,
        )

    def show_box(self,box, ax):
        x0, y0 = box[0], box[1]
        w, h = box[2] - box[0], box[3] - box[1]
        ax.add_patch(
            plt.Rectangle(
                (x0, y0), w, h, edgecolor="green", facecolor=(0, 0, 0, 0), lw=2
            )
        )

    def execute(self,img_path):
        self.img_path=img_path
        return self.produce_mask()