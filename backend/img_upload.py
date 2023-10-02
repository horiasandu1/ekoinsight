
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse  # Import JSONResponse
from BotCapabilities.ApiSfxReplicate import ApiSfxReplicate
from BotCapabilities.EkoInsightBot import EkoInsightBot
from BotCapabilities.LocalMask import LocalMask
from BotCapabilities.ApiImgDreamStudio import ApiImgDreamStudio
from BotCapabilities.ApiBlipReplicate import ApiBlipReplicate
from BotCapabilities.ApiChatGpt import ApiChatGpt
import os
import json


app = FastAPI()

# Define a directory to save the uploaded images

# sudo apt-add-repository ppa:redislabs/redis
# sudo apt-get update
# sudo apt-get upgrade
# sudo apt-get install redis-server
# sudo service redis-server restart


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

print("###### EkoInsightBot READY##########")

input_dir=config_data['input_paths']['imgs']

uploaded_image_filepath= None  # Initialize a global variable

@app.post("/upload/")
async def identify_image(file: UploadFile):
    print("upload detected")
    global uploaded_image_filepath  # Declare the global variable

    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        raise HTTPException(status_code=400, detail="Only image files (jpg, jpeg, png, gif) are allowed.")

    filename = f"uploaded_image_{os.urandom(4).hex()}.jpg"
    filepath = os.path.join(input_dir, filename)

    with open(filepath, "wb") as image_file:
        image_file.write(file.file.read())

    object_identification = img_identifier.execute(filepath)
    print("image identified")
    uploaded_image_filepath = filepath
    print(f"returning :{object_identification}")
    # Create a JSONResponse with a 200 status code
    return JSONResponse(content= {"description": object_identification}, status_code=200)

@app.post("/imagine/")
async def imagine_image(identified_object: str):
    print("imagine task detected")
    global filepath  # Declare the global variable
    if filepath is None:
        raise HTTPException(status_code=400, detail="No uploaded image found. Please upload an image first.")

    inpaint_path = ekoinsightbot.execute(filepath, identified_object=identified_object)

    # Create a JSONResponse with a 200 status code
    return JSONResponse(content={"inpaint_path": inpaint_path}, status_code=200)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)