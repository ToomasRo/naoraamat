import os
import sys
import json
from pathlib import Path
import dlib
from tqdm import tqdm
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_helper import resize_to_fhdish, process_image_multiple_faces
from utils.EShelper import ESclient, upload_unnamed_to_elastic
from utils.gdrive_integration import create_drive_service, list_folder_recursive

from dotenv import dotenv_values

config: dict = {
    **dotenv_values("backend/.env"),  # load shared development variables
    # **dotenv_values(".env.secret"),  # load sensitive variables
    # **os.environ,  # override loaded values with environment variables
}


def normalize_unicode(text):
    return unicodedata.normalize("NFKC", text)


def find_gdrive_id(folder_structure, filepath) -> str:
    for part in filepath.split("/")[:-1]:
        if "gdrive" in part:
            continue

        for listike in folder_structure:
            if normalize_unicode(listike["name"].lower()) == normalize_unicode(
                part.lower()
            ):
                folder_structure = listike["children"]
                break

    for pildike in folder_structure:
        if normalize_unicode(pildike["name"].lower()) == normalize_unicode(
            filepath.split("/")[-1].lower()
        ):
            return pildike["id"]

    return "None"


def upload_local_images(ESclient, folder_structure, folder):
    file_count = sum(
        len(files) for _, _, files in os.walk(folder)
    )  # Get the number of files
    with tqdm(total=file_count, ncols=100) as pbar:  # Do tqdm this way
        for root, _dirs, files in os.walk(folder):
            for f in files:
                if f == ".DS_Store":
                    continue

                image_path = os.path.join(root, f)
                temppath = image_path.removeprefix(folder)
                gdrive_id = find_gdrive_id(folder_structure, temppath)

                img = dlib.load_rgb_image(image_path)
                small_img, scale_factor = resize_to_fhdish(img)
                facedatas = process_image_multiple_faces(small_img)

                if not facedatas:
                    continue

                for facedata in facedatas:
                    face_loc, face_chip, face_descriptor = facedata

                    # print(f"uploading, {image_path=}, {gdrive_id=}")
                    upload_unnamed_to_elastic(
                        ESclient=ESclient,
                        index="unnamed",
                        face_vector=list(face_descriptor),
                        face_loc_img=face_loc,
                        gdrive_id=gdrive_id,
                        image_location=image_path,
                        scale_factor=scale_factor,
                    )

                pbar.update(1)


if __name__ == "__main__":
    drive_service = create_drive_service()

    if not Path("gdrive_data.json").exists():
        folder_structure = list_folder_recursive(drive_service, config["GDRIVE_FOLDER"])
        with open("gdrive_data.json", "w+", encoding="utf-8") as f:
            json.dump(folder_structure, f, ensure_ascii=False)
    else:
        with open("gdrive_data.json", "r", encoding="utf-8") as f:
            folder_structure = json.load(f)

    if not ESclient.indices.exists(index="unnamed"):
        from utils.EShelper import create_unnamed_index

        resp = create_unnamed_index(ESclient)
        print(resp)

    upload_local_images(ESclient, folder_structure, "data/reduced/")
