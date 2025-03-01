import pickle
import dlib
import os

from facedata import Face

TEMP_PATH = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/"
PREDICTOR_PATH = "models/shape_predictor_5_face_landmarks.dat" # sys.argv[1]
FOLDER_PATH = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/data/pildid/reduced/2024-l/" #Tartu L!E! ja noorliikmed Heino Pärn/
FACE_REC_MODEL_PATH = "models/dlib_face_recognition_resnet_model_v1.dat" # sys.argv[2]


def directory_traversal(path):
    for root, _dirs, files in os.walk(path):
        for f in files:
            yield root, f

def preprocess_images(input_folder=FOLDER_PATH, output_folder=TEMP_PATH, predictor_path=PREDICTOR_PATH, face_rec_model_path=FACE_REC_MODEL_PATH):
    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_path)
    facerec = dlib.face_recognition_model_v1(face_rec_model_path)


    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    if not os.path.exists(os.path.join(output_folder, "pickles")):
        os.mkdir(os.path.join(output_folder, "pickles"))



    for rootpth, image in directory_traversal(input_folder):
        face_file_path = os.path.join(rootpth, image)
        img = dlib.load_rgb_image(face_file_path)
        detects = detector(img, 1) # 1 is upsample image 1 time

        if len(detects) == 0:
            print(f"Sorry, there were no faces found in '{face_file_path}'")
            continue
        
        faces = dlib.full_object_detections()
        for detection in detects:
            faces.append(shape_predictor(img, detection))



        # TODO kuna kahjuks ei suuda get_face_chips ja save_face_chip koopereeruda, siis tuleb teha koleda while truega
        # probleem selles et face_chips[i] töötab, aga tal pole __iter__ defineeritud, ehk ei saa niisama salvestada
        # for idx, face_chip in enumerate(dlib.get_face_chips(img, faces, size=320)):
        #     print(type(face_chip), face_chip.shape)
        #     dlib.save_face_chip(img, face_chip, chip_filename=f"/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/{image}__{idx}")


        idx = 0
        while True:
            try:
                face_chip = dlib.get_face_chip(img, faces[idx])
                face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(face_chip)

                extra_dets = dlib.get_face_chip_details(faces[idx])

                customface = Face(extra_dets.rect, face_file_path, face_chip, face_descriptor_from_prealigned_image)
                with open(f"{output_folder}pickles/{image}_{idx}", "wb+") as f:
                    pickle.dump(customface, f, pickle.HIGHEST_PROTOCOL)
                dlib.save_face_chip(img, faces[idx], chip_filename=f"{output_folder}{image}_{idx}", padding=0.5)
            
            except IndexError as ie:
                # print(f"kõik näod salvestatud, {face_file_path}")
                break
            idx+=1

        # BACKUP
        # idx = 0
        # while True:
        #     try:
                
        #         dlib.save_face_chip(img, faces[idx], chip_filename=f"/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/{image}__{idx}", padding=0.5)
        #     except IndexError as ie:
        #         # print(f"kõik näod salvestatud, {face_file_path}")
        #         break
        #     idx+=1
