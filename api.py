import csv
import os
import secrets
import shutil
from pathlib import Path
from time import localtime, strftime

from fastapi import FastAPI, Response, UploadFile
from pdf2image import convert_from_bytes

from src.entry import entry_point

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

    random_path = generate_random_str()
    current_omrs_path = generate_random_path(random_path)
    convert_to_images(file, current_omrs_path)

    run_omr_checker(current_omrs_path, random_path)

    results = result_csv_to_json(random_path)

    cleanup()

    return results


def convert_to_images(file: UploadFile, output_dir: str):
    os.makedirs(f"{output_dir}/sheet", exist_ok=True)
    images = convert_from_bytes(
        file.file.read(), dpi=100, fmt="jpeg", use_pdftocairo=True, thread_count=4
    )
    for i, image in enumerate(images):
        image.save(f"{output_dir}/sheet/student_{i+1}.png", "PNG")


def generate_random_path(random_path: str):
    images_output_path = f"omr_inputs/{random_path}"
    shutil.copytree("samples/said", images_output_path)
    return images_output_path


def generate_random_str(length: int = 10):
    return secrets.token_hex(length)


def run_omr_checker(input_dir: str, output_dir: str):
    args = {
        "input_paths": [input_dir],
        "debug": False,
        "output_dir": f"outputs/{output_dir}",
        "autoAlign": False,
        "setLayout": False,
    }
    for root in args["input_paths"]:
        entry_point(
            Path(root),
            args,
        )


def result_csv_to_json(random_path: str):
    TIME_NOW_HRS = strftime("%I%p", localtime())
    result_csv_path = f"outputs/{random_path}/sheet/Results/Results_{TIME_NOW_HRS}.csv"
    with open(result_csv_path, "r") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    return rows


def cleanup():
    shutil.rmtree("omr_inputs")
    shutil.rmtree("outputs")
    os.makedirs("omr_inputs")
    os.makedirs("outputs")
