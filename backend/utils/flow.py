from ast import arg

from numpy import isin
import image_helper
import gdrive_integration
import EShelper
import time
import cv2

import os

import threading
import mimetypes

import threading, time
import tqdm

import json
with open("data.json", "r") as f:
    FOLDER_STRUCTURE = json.load(f)

def directory_traversal(path):
    for root, _dirs, files in os.walk(path):
        for f in files:
            yield (root, f)


def process_from_gdrive(args):
    file_id, friendly_name = args
    print(friendly_name)

    if "Suvepäevad" in friendly_name:
        return
    if "PP0117" in friendly_name:
        return
    if "Jõusaal" in friendly_name:
        return
    
    drive_service = gdrive_integration.create_drive_service() # TODO iga kord luua on raiskamine

    nparr = gdrive_integration.download_file(drive_service, file_id)
    matlike, scale_factor = image_helper.resize_to_fhdish(nparr)
    faces_datas = image_helper.process_image_multiple_faces(matlike)
    if faces_datas == 0:
        return

    for facedata in faces_datas:
        EShelper.upload_unnamed_to_elastic2(
            esclient,
            index="unnamed",
            face_vector=list(facedata[2]),
            face_loc_img=facedata[0],
            gdrive_id=file_id,
            human_friendly_loc=friendly_name,
            scale_factor=scale_factor,
        )
    time.sleep(0.5)

def find_gdrive_id(folder_structure, filepath)->str:
    for part in filepath.split("/")[:-1]:
        # print(part)
        if "gdrive" in part: 
            continue
    
        for listike in folder_structure:
            if listike["name"] == part:
                folder_structure = listike["children"]
    for pildike in folder_structure:
        if pildike["name"].lower() == filepath.split("/")[-1].lower():
            # print(pildike["id"])
            return pildike["id"]
        
    return "None"





def process_from_mount(filtuple):


    filepath = os.path.join(filtuple[0], filtuple[1])
    print(filepath)

    big_matlike = cv2.imread(filepath)
    if big_matlike is None:
        return

    matlike, scale_factor = image_helper.resize_to_fhdish(big_matlike)
    faces_datas = image_helper.process_image_multiple_faces(matlike)
    print(f"Found {0 if faces_datas==0 else len(faces_datas)} faces in {filepath}")

    if faces_datas == 0:
        return

    
    for facedata in faces_datas:
        EShelper.upload_unnamed_to_elastic2(
            esclient,
            index="unnamed",
            face_vector=list(facedata[2]),
            face_loc_img=facedata[0],
            gdrive_id=find_gdrive_id(FOLDER_STRUCTURE, filepath),
            human_friendly_loc=filepath,
            scale_factor=scale_factor,
        )

# if __name__ == "__main__":
#     filepath = os.path.join("gdrive/Suvepäevad/Suvepäevad - Heino Pärn", "2W6A7551.jpg")
#     import json
#     with open("data.json", "r") as f:
#         folder_structure = json.load(f)
#     find_gdrive_id(folder_structure, filepath)

if __name__ == "__main__":

    esclient = EShelper.ESclient

    probleemsed = []

    # done = [
        # 'EÜS ja CSE ühiste tantsukursuste avapidu',
        # 'Märg Surm 13',
        # 'Jõusaal Karl Kask'
        # "Tln knd pildistamine Marko Krund",
        # 'EÜS nrl! ja Amicita reb!! ühine veinilaud teemal "Poola piiri ääres"',
        # "Tartu L!E! ja noorliikmed Heino Pärn",
        # 'Tallinna veinilaud Heino Pärn',
        # 'Volber - Heino Pärn',
        # "EÜS ja C!FP piknik",
        # "I külalisõhtu Tartus Erko Olumets",
        # "EV106",
        # 'Aastapäev',
        # 'Ak! orgide õllelaud Heino Pärn',
    # ]
    folders = [
        'Konvendituur Tallinn - Heino Pärn',
        'Auvil! Männi värvivara üleandmine',
        # 'PPO Kesäretki Heino Pärn',
        # 'Tartu laulupidu Heino Pärn',
    ]
    for bigfolder in folders:
        for root, filename in tqdm.tqdm(
            directory_traversal(f"gdrive/{bigfolder}"), desc=f"{bigfolder}"
        ):
            # print(root)
            # print(filename)

            # try:
            process_from_mount((root, filename))

            # except Exception as e:
            #     print(filename, e)
            #     probleemsed.append([os.path.join(root, filename), e])

            # input("edasi?")
            print("------------")

    # # threads = []
    # # for file in directory_traversal("./gdrive"):
    # #     t = threading.Thread(target=process_from_mount, args=(file,))
    # #     t.start()
    # #     threads.append(t)

    # # for thread in threads:
    # #     thread.join()

    # jobs = Queue()
    # for file in directory_traversal("./gdrive/Tallinna veinilaud Heino Pärn"):
    #     jobs.put(file)

    # for i in range(1):
    #     worker = threading.Thread(target=do_stuff, args=(jobs,))
    #     worker.start()

    # print("waiting for queue to complete", jobs.qsize(), "tasks")
    # jobs.join()
    # print("all done")

    for p in probleemsed:
        print(p)

    print("------------------------------------------------------")
    for p in probleemsed:
        print(p[0])
