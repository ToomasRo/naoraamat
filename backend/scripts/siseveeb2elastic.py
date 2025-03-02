"""
Processes all images from a folder to an elasticsearch index.

Meant to use for photos where the name of the person in the photo is known.

Prerequisites:
    - A folder which has photo examples of people:
        - FOLDER_PATH
            |- Lastname, First name(s)
                |- img1.png etc
    - 
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_helper import resize_to_fhdish, process_image_multiple_faces
from utils.EShelper import ESclient, upload_named_face_to_elastic

import dlib


FOLDER_PATH = "data/siseveeb/"


def directory_traversal(path):
    for root, _dirs, files in os.walk(path):
        for f in files:
            yield root, f


from tqdm import tqdm

if __name__ == "__main__":

    if not ESclient.indices.exists(index="siseveeb1"):
        from utils.EShelper import create_named_index

        resp = create_named_index(ESclient)
        print(resp)

    print("alustame failide söömisega")

    for root, file in tqdm(directory_traversal(FOLDER_PATH), total=1387):
        if root == FOLDER_PATH:
            continue

        last_name = root.split("/")[-1].split(" ")[0]
        firstname = " ".join(root.split("/")[-1].split(" ")[1:])

        face_file_path = os.path.join(root, file)

        img = dlib.load_rgb_image(face_file_path)
        small_img, scale_factor = resize_to_fhdish(img)
        facedatas = process_image_multiple_faces(small_img)

        if not facedatas:
            continue

        for facedata in facedatas:
            face_loc, face_chip, face_descriptor = facedata

            upload_named_face_to_elastic(
                ESclient=ESclient,
                index="siseveeb1",
                face_vector=list(face_descriptor),
                first_name=firstname,
                last_name=last_name,
                image_loc="data-ingest",
                face_loc_img=face_loc,
                scale_factor=scale_factor,
                org="Eesti Üliõpilaste Selts",
            )
