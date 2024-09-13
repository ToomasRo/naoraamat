from elasticsearch import Elasticsearch
import pickle
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
    output_folder=TEMP_PATH,
    predictor_path=PREDICTOR_PATH,
    face_rec_model_path=FACE_REC_MODEL_PATH,
):
    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_path)
    facerec = dlib.face_recognition_model_v1(face_rec_model_path)

    for rootpth, image in directory_traversal(input_folder):
        face_file_path = os.path.join(rootpth, image)
        img = dlib.load_rgb_image(face_file_path)
        detects = detector(img, 1)  # 1 is upsample image 1 time

        if len(detects) == 0:
            print(f"Sorry, there were no faces found in '{face_file_path}'")
            continue

        faces = dlib.full_object_detections()
        for detection in detects:
            faces.append(shape_predictor(img, detection))

        idx = 0
        while True:
            try:
                face_chip = dlib.get_face_chip(img, faces[idx])
                face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(
                    face_chip
                )

                extra_dets = dlib.get_face_chip_details(faces[idx])

                # customface = Face(extra_dets.rect, face_file_path, face_chip, face_descriptor_from_prealigned_image)
                # with open(f"{output_folder}pickles/{image}_{idx}", "wb+") as f:
                #     pickle.dump(customface, f, pickle.HIGHEST_PROTOCOL)
                # dlib.save_face_chip(img, faces[idx], chip_filename=f"{output_folder}{image}_{idx}", padding=0.5)

            except IndexError as ie:
                # print(f"kõik näod salvestatud, {face_file_path}")
                break
            idx += 1


detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor(PREDICTOR_PATH)
facerec = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)


def process_image(
    face_file_path,
    # predictor_path=PREDICTOR_PATH,
    # face_rec_model_path=FACE_REC_MODEL_PATH,
):
    """Leiab pildilt täpselt 1 näo ning tagastab andmed

    :param str face_file_path: faili asukoht
    :param os.path predictor_path: kus dlib predictor asub, defaults to PREDICTOR_PATH
    :param os.path face_rec_model_path: kus dlib face_rec asub, defaults to FACE_REC_MODEL_PATH
    :return tuple: face location within image, face chip, face vector
    """
    global shape_predictor, facerec, detector

    img = dlib.load_rgb_image(face_file_path)
    detects = detector(img, 1)  # 1 is upsample image 1 time

    if len(detects) == 0:
        print(f"Sorry, there were no faces found in '{face_file_path}'")
        return 0
    elif len(detects) != 1:
        print(
            f"Sorry, there were too many ({len(detects)}) faces found in '{face_file_path}'"
        )
        return 0

    faces = dlib.full_object_detections()
    for detection in detects:
        faces.append(shape_predictor(img, detection))

    idx = 0

    face_chip = dlib.get_face_chip(img, faces[idx])
    face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(face_chip)

    extra_dets = dlib.get_face_chip_details(faces[idx])

    return (
        extra_dets.rect,
        face_chip,
        face_descriptor_from_prealigned_image,
    )


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

# docker exec fastapi-application sh -c "echo hello"

"""
#create index
PUT /my-index
{
  "mappings": {
    "properties": {
      "vector": {
        "type": "dense_vector",
        "dims": 3
      },
      "text": {
        "type": "text"
      }
    }
  }
}

#ingest data
POST /my-index/_doc
{ 
  "vector": [1, 5, -20], 
  "text": "hello world" 
}

#perform vector search
POST /my-index/_search
{
  "size" : 3,
  "query" : {
    "knn": {
      "field": "vector",
      "query_vector": [1, 5, -20]
    }
  }
}






#     """

# curl -v -H 'X-API-TOKEN'='X0pMaTE1RUJVNFdIU3NjOHRIS2E6RHg5VTZlZHJSMW0yNXRpZkhwVXhfQQ==' https://seltsi_naoraamat-elastic-1:9200/my-index

# curl -H "Authorization: ApiKey X0pMaTE1RUJVNFdIU3NjOHRIS2E6RHg5VTZlZHJSMW0yNXRpZkhwVXhfQQ==" https://seltsi_naoraamat-elastic-1:9200/my-index
# curl -v -H "Authorization: ApiKey X0pMaTE1RUJVNFdIU3NjOHRIS2E6RHg5VTZlZHJSMW0yNXRpZkhwVXhfQQ==" https://host.docker.internal:9200/my-index

# client = Elasticsearch("https://host.docker.internal:9200", api_key="X0pMaTE1RUJVNFdIU3NjOHRIS2E6RHg5VTZlZHJSMW0yNXRpZkhwVXhfQQ==")
