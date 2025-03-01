import io
import re
import numpy as np
from dotenv import dotenv_values
import time
import json

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

from tqdm import tqdm

import cv2 
import os 
import sys
sys.path.append('../') # TODO mitte relative importe kasutada
from backend.utils import image_helper
import backend.utils.EShelper


config: dict = {
    **dotenv_values("backend/.env"),  # load shared development variables
    # **dotenv_values(".env.secret"),  # load sensitive variables
    # **os.environ,  # override loaded values with environment variables
}
GDRIVE_CERT_PATH = "certs/seltsi-naoraamat-a62787628fe0.json"



def create_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        GDRIVE_CERT_PATH,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=creds)


def list_folder_recursive(drive_service, folder_id, top_level=False):
    page_token = None
    items = []
    while True:
        results = (
            drive_service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType)",
                orderBy="createdTime",  # TODO kas see funkab
                pageToken=page_token,
            )
            .execute()
        )
        time.sleep(0.5)
        items.extend(results.get("files", []))

        page_token = results.get("nextPageToken", None)
        if page_token is None:
            break
    
    for asi in items:
        if "mimeType" in asi:
            if asi["mimeType"] == "application/vnd.google-apps.folder":
                print(asi["name"])
                asi["children"] = list_folder_recursive(drive_service, asi["id"])
    return items


def download_file(drive_service, file_id: str) -> np.ndarray:
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()  # keeping in memory
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))

    return np.frombuffer(fh.getvalue(), np.uint8)


def parkur_childs(childrenlist, parent_name=""):
    for child in childrenlist:
        if child["mimeType"].startswith("image"):
            # print(child["id"], parent_name + "/" + child["name"])
            yield child["id"], parent_name + "/" + child["name"], child["mimeType"]
        elif child["mimeType"] == "application/vnd.google-apps.folder":
            yield from parkur_childs(
                child["children"], parent_name + "/" + child["name"]
            )
    return 0


def yield_id_from_structure(folder_structure, folder_name):
    for big_guy in folder_structure:
        # print(big_guy["name"])
        if not "children" in big_guy:
            continue
        yield from parkur_childs(
            big_guy["children"], f"{folder_name}/{big_guy['name']}"
        )
    return 0




def scale_down(basepath, newpath, gdrive_structure):
    id_and_path = yield_id_from_structure(gdrive_structure, basepath)
    id_and_path_and_scalefactor = []
    for file_id, filepath, mimetype in tqdm(id_and_path, total=13681):
        # print(file_id, filepath)
        if mimetype == "image/jpeg" or mimetype == "image/png":
            try:
                suur_pilt = cv2.imread(filepath)
                resized_img, scaling_factor = image_helper.resize_to_fhdish(suur_pilt)

                new_file_path = re.sub(basepath, newpath, filepath)
                if not os.path.exists(os.path.dirname(new_file_path)):
                    os.makedirs(os.path.dirname(new_file_path))
                # print(new_file_path)
                cv2.imwrite(new_file_path, resized_img)

                id_and_path_and_scalefactor.append((file_id, new_file_path, scaling_factor))
            except Exception as e:
                print(e)
                print(f"Failed to process {filepath}")
                continue
            
    return id_and_path_and_scalefactor



def find_faces_and_put_elastic(gid_path_scale):
    # loeme miniaturiseeritud failid (basepath/reduced), 
    # leiame näod ja paneme elastikusse
    global es_client
    for row in tqdm(gid_path_scale):

        gdrive_id, filepath, scale = row
        scale = float(scale)

        faces = image_helper.process_image_multiple_faces(cv2.imread(filepath))
        if faces == 0: return # see ei leidnud ühtegi nägu
        for coords, _chip, descriptor in faces:
            backend.utils.EShelper.upload_unnamed_to_elastic2(es_client, 
                                                  "unnamed",
                                                  face_vector=descriptor,
                                                  face_loc_img=coords,
                                                  gdrive_id=gdrive_id,
                                                  human_friendly_loc=filepath,
                                                  scale_factor=scale,
                                                  )
    pass

def main():
    # salvestab vastava kausta struktuuri faili
    folder_id = "1vICkLhQhzfdBgL4EoNULmZmj7u_TbiY2"  # folder EÜS
    drive_service = create_drive_service()

    folder_structure = list_folder_recursive(
        drive_service, folder_id,
        top_level=True
    )

    with open("gdrive_structure.json", "w+") as f:
        json.dump(folder_structure, f)

    # loeb vastava salvestatud struktuuri ja paneb kokku path & id
    with open("gdrive_structure.json", "r") as f:
        folder_structure = json.load(f)
    
    for i in yield_id_from_structure(folder_structure, "data/pildid"):
        print(i)

    gid_path_scale = scale_down("data/pildid", "data/pildid/reduced", folder_structure)

    with open("gid_path_scale.txt", "w+") as f:
        for row in gid_path_scale:
            f.write(f"{';'.join(row)}\n")

    pass

es_client = backend.utils.EShelper.ESclient

if __name__ == "__main__":

    # main()

    with open("gid_path_scale.txt", "r") as f:
        data = f.readlines()
    

    backend.utils.EShelper.create_unnamed_index(es_client)
    find_faces_and_put_elastic(data)
    ...




