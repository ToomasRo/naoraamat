from ast import Break
from elasticsearch import Elasticsearch
import dlib
import os


TEMP_PATH = "seltsi_naoraamat/backend/temp/"
PREDICTOR_PATH = "./models/shape_predictor_5_face_landmarks.dat"
FOLDER_PATH = "/seltsi_naoraamat/backend/data/siseveeb/"
FACE_REC_MODEL_PATH = "./models/dlib_face_recognition_resnet_model_v1.dat"


def directory_traversal(path):
    for root, _dirs, files in os.walk(path):
        for f in files:
            yield root, f


def preprocess_images(
    input_folder=FOLDER_PATH,
):
    res = []
    for rootpth, image in directory_traversal(input_folder):
        face_file_path = os.path.join(rootpth, image)

        temp_res = process_image_multiple_faces(face_file_path)
        if temp_res != 0:
            res.extend(temp_res)
    return res


detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(PREDICTOR_PATH)
facerec = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)


def process_image_multiple_faces(
    face_file_path,
):
    """Leiab pildilt täpselt mitu nägu ning tagastab listi, kus iga element on

    :param str face_file_path: faili asukoht
    :param os.path predictor_path: kus dlib predictor asub, defaults to PREDICTOR_PATH
    :param os.path face_rec_model_path: kus dlib face_rec asub, defaults to FACE_REC_MODEL_PATH
    :return list: [[face location within image, face chip, face vector], ...]
    """
    global shape_predictor, facerec, detector

    img = dlib.load_rgb_image(face_file_path)
    detects = detector(img, 1)  # 1 is upsample image 1 time

    if len(detects) == 0:
        print(f"Sorry, there were no faces found in '{face_file_path}'")
        return 0

    faces = dlib.full_object_detections()
    for detection in detects:
        faces.append(shape_predictor(img, detection))

    idx = 0
    result = []
    while True:
        try:
            face_chip = dlib.get_face_chip(img, faces[idx])
            face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(
                face_chip
            )

            extra_dets = dlib.get_face_chip_details(faces[idx])
            x1 = int(extra_dets.rect.tl_corner().x)
            y1 = int(extra_dets.rect.tl_corner().y)

            x2 = int(extra_dets.rect.br_corner().x)
            y2 = int(extra_dets.rect.br_corner().y)

            result.append(
                (
                    [x1, y1, x2, y2],
                    face_chip,
                    face_descriptor_from_prealigned_image,
                )
            )
        except IndexError as ie:
            print(f"No more faces in {face_file_path}. Found {idx}")
            break
        idx += 1

    return result


def upload_to_elastic(
    ESclient: Elasticsearch,
    index,
    face_vector,
    image_loc,
    face_loc_img,
    scale_factor=1.0,
):
    resp1 = ESclient.index(
        index=index,
        document={
            "face_vector": face_vector,
            "face_location_in_image": face_loc_img,
            "image_location": image_loc,
            "scale_factor": scale_factor,
        },
    )
    return resp1


def create_index(client: Elasticsearch):
    settings = {"index.default_pipeline": "ingest_with_dates"}

    client.ingest.put_pipeline(
        id="ingest_with_dates",
        processors=[{"set": {"field": "created_at", "value": "{{_ingest.timestamp}}"}}],
    )

    resp = client.indices.create(
        index="unnamed",
        mappings={
            "properties": {
                "face_vector": {"type": "dense_vector", "dims": 128},
                "face_location_in_image": {"type": "keyword"},
                "image_location": {"type": "text"},
                "scale_factor": {"type": "float"},
            }
        },
        settings=settings,
    )
    return resp


if __name__ == "__main__":

    key = "d3c4SzI1RUI5TUpaRnl6V0U5UEE6aVlNZG9LVG1SVzIyZnZvUjVvaGROdw=="

    client = Elasticsearch(
        "https://host.docker.internal:9200",
        api_key="d3c4SzI1RUI5TUpaRnl6V0U5UEE6aVlNZG9LVG1SVzIyZnZvUjVvaGROdw==",
        verify_certs=False,
    )

    client.indices.create(index="my_index")
    client.index(
        index="my_index",
        id="my_document_id",
        document={
            "foo": "foo",
            "bar": "bar",
        },
    )
