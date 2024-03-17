import os
import secrets
import shutil

from fastapi import FastAPI, Response, UploadFile
from pdf2image import convert_from_bytes

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/check_omrs")
def check_omrs(file: UploadFile, response: Response):
    if (
        not file.filename.endswith(".pdf")
        and not file.content_type == "application/pdf"
    ):
        response.status_code = 400
        return {"message": "File must be a PDF"}

    current_omrs_path = generate_random_path()
    convert_to_images(file, current_omrs_path)

    return {"message": "Check OMRs"}


def convert_to_images(file: UploadFile, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_bytes(file.file.read())
    for i, image in enumerate(images):
        image.save(f"{output_dir}/sheet/student_{i+1}.png", "PNG")


def generate_random_path():
    random_path = generate_random_str()
    images_output_path = f"omr_inputs/{random_path}"
    shutil.copytree("samples/said", images_output_path)
    return images_output_path


def generate_random_str(length: int = 10):
    return secrets.token_hex(length)
