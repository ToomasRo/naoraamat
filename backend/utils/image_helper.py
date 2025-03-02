""" Piltidega töötlemised siin failis

resize_to_fhdish -> võtab 4k pildi ja teeb sellest 1080p pildi
process_image_multiple_faces -> võtab pildi ja tagastab listi, kus iga element on [face location within image, face chip, face vector]
"""

from typing import Literal
import cv2
import numpy as np
import dlib


WANTED_WIDTH = 1920
WANTED_HEIGHT = 1080

PREDICTOR_PATH = "./models/shape_predictor_5_face_landmarks.dat"
FACE_REC_MODEL_PATH = "./models/dlib_face_recognition_resnet_model_v1.dat"

detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(PREDICTOR_PATH)
facerec = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)


def resize_to_fhdish(img_array: np.ndarray | cv2.typing.MatLike):
    try:
        img_array = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception as e:
        img_array = img_array

    height, width = img_array.shape[:2]

    width_scaling_factor = WANTED_WIDTH / float(width)
    height_scaling_factor = WANTED_HEIGHT / float(height)

    scaling_factor = min(width_scaling_factor, height_scaling_factor)
    if abs(1 - scaling_factor) < 0.25:
        # no point in scaling down only by little
        return img_array, 1
    
    # if we need to upscale then do not scale and return 
    if scaling_factor > 1:
        return img_array, 1

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    # Resize the image using the INTER_AREA interpolation for better quality on downscaling
    resized_img = cv2.resize(
        img_array, (new_width, new_height), interpolation=cv2.INTER_AREA
    )

    return resized_img, scaling_factor


def process_image_multiple_faces(
    vaike_pilt: np.ndarray,
) -> list[tuple] | Literal[0]:
    """Leiab pildilt täpselt mitu nägu ning tagastab listi, kus iga element on

    :param np.ndarray img_array: numpy maatriks millest on võimalik välja lugeda pilt
    :return list[tuple]: [[face location within image, face chip, face vector], ...]
    """
    global shape_predictor, facerec, detector

    # vaike_pilt = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    # vaike_pilt = resize_to_fhdish(suur_pilt)

    detects = detector(vaike_pilt, 1)  # 1 is upsample image 1 time

    if len(detects) == 0:
        # print("Sorry, there were no faces found in")
        return 0

    faces = dlib.full_object_detections()
    for detection in detects:
        faces.append(shape_predictor(vaike_pilt, detection))

    idx = 0
    result = []
    while True:
        try:
            face_chip = dlib.get_face_chip(vaike_pilt, faces[idx])
            face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(
                face_chip
            )

            x1 = int(detects[idx].tl_corner().x)
            y1 = int(detects[idx].tl_corner().y)
            x2 = int(detects[idx].br_corner().x)
            y2 = int(detects[idx].br_corner().y)

            result.append(
                (
                    [x1, y1, x2, y2],
                    face_chip,
                    face_descriptor_from_prealigned_image,
                )
            )
        except IndexError as ie:
            # print(f"No more faces. Found {idx}")
            break
        idx += 1

    return result


if __name__ == "__main__":
    from gdrive_integration import download_file, create_drive_service

    from_net = True
    if from_net:
        nparr = download_file(
            create_drive_service(), "13AIvwtNKiChBv7FleWsq9EDm4Sb92gwE"
        )
        suur_pilt = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        suur_pilt = cv2.imread("pilt.jpg")
