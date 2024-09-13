import os
from dotenv import dotenv_values
import time

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload

import io

import cv2
import numpy as np



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

def list_folder_recursive(drive_service, folder_id):
    page_token = None
    items = []
    while True:
        results = (
            drive_service.files()
            .list(
                q=f"'{folder_id}' in parents",
                pageSize=10,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            )
            .execute()
        )
        # TODO see sisse panna
        # time.sleep(1)
        items.extend(results.get("files", []))

        page_token = results.get("nextPageToken", None)
        # TODO see välja võtta
        page_token = None
        if page_token is None:
            break

    for asi in items:
        if "mimeType" in asi:
            if asi["mimeType"] == "application/vnd.google-apps.folder":
                asi["children"] = list_folder_recursive(drive_service, asi["id"])
    return items


def download_file(drive_service, file_id:str)-> np.ndarray:
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
            yield child["id"], parent_name + "/" + child["name"]
        elif child["mimeType"] == "application/vnd.google-apps.folder":
            yield from parkur_childs(
                child["children"], parent_name + "/" + child["name"]
            )
        # elif child["mimeType"].startswith("video"):
        #     print(
        #         "video on", parent_name + "/" + child["name"], "aga ei protsessi seda"
        #     )
        # else:
        #     print(" midagi on katki", type(child))
        #     assert 2 == 0
    return 0


def yield_id_from_structure(folder_structure, folder_name):
    for big_guy in folder_structure:
        # print(big_guy["name"])
        yield from parkur_childs(
            big_guy["children"], f"{folder_name}/{big_guy['name']}"
        )
    return 0


if __name__ == "__main__":

    folder_id = "1WxBddD-wXkEv6b4gqM7eojZqw4GK4Sn9"  # rongkäik
    folder_id = "1ymsPl1dUSXi3FwHnk3tAi3cozyUJGrAE"  # folder folder 13f2mnC_SwiyuC-q8Jv3orVLA8G5RNO94
    folder_id = "13f2mnC_SwiyuC-q8Jv3orVLA8G5RNO94"  # folder 2106-I

    # failid_kokku = list_folder_recursive(drive_service, "14L-QPf1Phs2h8i5XYeEC-LpAJ6TheOqG")

    drive_service = create_drive_service()

    # numpy_img = download_file(drive_service, "1cuHDR2wloqCtMzgfgwZ7O335srci0SED")
    # img = cv2.imdecode(numpy_img, 1)

    folder_structure = list_folder_recursive(drive_service, "14L-QPf1Phs2h8i5XYeEC-LpAJ6TheOqG")
    for _id, friendly_name in yield_id_from_structure(folder_structure, "2024-I"):
        print(friendly_name)


# https://drive.google.com/file/d/{file_id}/view
# https://drive.google.com/drive/folders/{folder_id}

# python3 utils/gdrive_integration.py
