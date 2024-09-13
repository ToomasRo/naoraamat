# TODO siia koguda kõik ESclientiga seotud funktsioonid
from elasticsearch import Elasticsearch


ESclient = Elasticsearch(
    "https://host.docker.internal:9200",
    api_key="d3c4SzI1RUI5TUpaRnl6V0U5UEE6aVlNZG9LVG1SVzIyZnZvUjVvaGROdw==",
    verify_certs=False,
)


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
            }
        },
        settings=settings,
    )
    return resp


def upload_named_face_to_elastic(
    ESclient: Elasticsearch,
    index,
    face_vector,
    first_name,
    last_name,
    image_loc,
    face_loc_img,
):
    resp1 = ESclient.index(
        index=index,
        document={
            "face_vector": face_vector,
            "face_location_in_image": face_loc_img,
            "first_name": first_name,
            "last_name": last_name,
            "image_location": image_loc,
        },
    )
    return resp1


def delete_index(client: Elasticsearch, index_name: str):
    return client.indices.delete(index=index_name)


def create_named_index(client: Elasticsearch):
    settings = {"index.default_pipeline": "ingest_with_dates"}

    client.ingest.put_pipeline(
        id="ingest_with_dates",
        processors=[{"set": {"field": "created_at", "value": "{{_ingest.timestamp}}"}}],
    )

    resp = client.indices.create(
        index="named-index",
        mappings={
            "properties": {
                "face_vector": {"type": "dense_vector", "dims": 128},
                "face_location_in_image": {"type": "keyword"},
                "first_name": {"type": "text"},
                "last_name": {"type": "text"},
                "image_location": {"type": "text"},
            }
        },
        settings=settings,
    )
    return resp


def search_elastic_siseveeb(first, last):
    return ESclient.search(
        index="named-index",
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


def search_elastic_sarnased(first, last):
    return ESclient.search(
        index="named-index",
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
    )
