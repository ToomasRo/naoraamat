# TODO siia koguda kõik ESclientiga seotud funktsioonid
from elasticsearch import Elasticsearch

from dotenv import dotenv_values

# TODO remove before prod
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
from elasticsearch.exceptions import ElasticsearchWarning

warnings.simplefilter("ignore", ElasticsearchWarning)

config: dict = {
    **dotenv_values(".env"),  # load shared development variables
    # **dotenv_values(".env.secret"),  # load sensitive variables
    # **os.environ,  # override loaded values with environment variables
}

ESclient = Elasticsearch(
    "https://localhost:9200",
    api_key=config["ELASTIC_API_KEY"],
    verify_certs=False,
)


def upload_unnamed_to_elastic(
    ESclient: Elasticsearch,
    index: str,
    face_vector: list,
    face_loc_img: list,
    gdrive_id: str,
    image_location: str,
    scale_factor=1.0,
    version=1,
):
    return ESclient.index(
        index=index,
        document={
            "face_vector": face_vector,
            "face_location_in_image": face_loc_img,
            "gdrive_id": gdrive_id,
            "image_location": image_location,
            "scale_factor": scale_factor,
            "version": version,
        },
    )


def upload_named_face_to_elastic(
    ESclient: Elasticsearch,
    index,
    face_vector,
    first_name,
    last_name,
    image_loc,
    face_loc_img,
    scale_factor,
    org,
    version=1,
):
    return ESclient.index(
        index=index,
        document={
            "face_vector": face_vector,
            "face_location_in_image": face_loc_img,
            "first_name": first_name,
            "last_name": last_name,
            "image_location": image_loc,
            "scale_factor": scale_factor,
            "organisation": org,
            "version": version,
        },
    )


def create_unnamed_index(client: Elasticsearch):
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
                "gdrive_id": {"type": "text"},
                "version": {"type": "long"},
            }
        },
        settings=settings,
    )
    return resp


def create_named_index(client: Elasticsearch):
    settings = {"index.default_pipeline": "ingest_with_dates"}

    client.ingest.put_pipeline(
        id="ingest_with_dates",
        processors=[{"set": {"field": "created_at", "value": "{{_ingest.timestamp}}"}}],
    )

    resp = client.indices.create(
        index="siseveeb1",
        mappings={
            "properties": {
                "face_vector": {"type": "dense_vector", "dims": 128},
                "face_location_in_image": {"type": "keyword"},
                "first_name": {"type": "text"},
                "last_name": {"type": "text"},
                "image_location": {"type": "text"},
                "scale_factor": {"type": "float"},
                "organisation":{"type":"text"},
                "version": {"type": "long"},
            }
        },
        settings=settings,
    )
    return resp


def delete_index(client: Elasticsearch, index_name: str):
    return client.indices.delete(index=index_name)


def search_elastic_by_name(first, last, index="siseveeb1"):
    return ESclient.search(
        index=index,
        query={
            "bool": {
                "should": [
                    {"match": {"first_name": first}},
                    {"match": {"last_name": last}},
                ],
                "minimum_should_match": 2,
            }
        },
        track_total_hits=True,
        # source_includes=["face_vector"],
    )


def search_elastic_similarity(index, fv):
    return  ESclient.search(
                index=index,
                knn={
                    "field": "face_vector",
                    "query_vector": fv,
                    "k": 10,
                    "num_candidates": 100,
                },
                source_includes=["image_location"],
                source=False,
            )
