import os
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from utils import EShelper
from utils.EShelper import ESclient
from utils.EShelper import (
    search_elastic_siseveeb,
    search_elastic_sarnased,
    create_named_index,
    upload_named_face_to_elastic,
    create_unnamed_index,
    upload_unnamed_to_elastic,
)

from utils import scan_known_faces_to_elastic, scan_unknown


# TODO remove before prod
import urllib3
import warnings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from elasticsearch.exceptions import ElasticsearchWarning

warnings.simplefilter("ignore", ElasticsearchWarning)


app = FastAPI()
app.mount("/static", StaticFiles(directory="./data", html=True), name="static")


# TODO decide what frontend
origins = [
    "http://localhost:4200",
    "localhost:4200",
    "https://drive.google.com",
    "https://play.google.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello_world():
    return {"message": "OK"}


@app.get("/create-index")
def create_index():
    ret = create_named_index(ESclient)
    return {"message": f"{ret}"}


@app.get("/delete-index")
def delete_index():
    ret = EShelper.delete_index(ESclient, "named-index")
    return {"message": f"{ret}"}


@app.get("/ingest-siseveeb")
def ingest_siseveeb():
    start = time.time()
    for asi in scan_known_faces_to_elastic.directory_traversal("data/siseveeb"):
        print(asi)
        result = scan_known_faces_to_elastic.process_image(
            os.path.join(*asi)
        )  # face location within image, face chip, face vector
        if result == 0:
            continue
        else:
            print(result[0], result[2][0])
            last_name, first_name = asi[0].split("/")[-1].split(", ")
            x1 = int(result[0].tl_corner().x)
            y1 = int(result[0].tl_corner().y)

            x2 = int(result[0].br_corner().x)
            y2 = int(result[0].br_corner().y)

            res2 = upload_named_face_to_elastic(
                ESclient,
                index="named-index",
                face_vector=list(result[2]),
                first_name=first_name,
                last_name=last_name,
                image_loc=os.path.join(*asi),
                face_loc_img=[x1, y1, x2, y2],
            )
            print(res2)

    return {"message": f"{time.time()-start}"}


@app.get("/find_siseveeb")
def find_seltsivend(first=str, last=str):
    resp = search_elastic_siseveeb(first, last)

    face_vectors = []
    for doc in resp["hits"]["hits"]:
        face_vectors.append(doc["_source"]["face_vector"])

    resps = []
    for fv in face_vectors:
        resps.append(
            ESclient.search(
                index="named-index",
                knn={
                    "field": "face_vector",
                    "query_vector": fv,
                    "k": 10,
                    "num_candidates": 100,
                },
                source_includes=["image_location"],
                source=False,
            )
        )

    score_and_loc = []
    for resp in resps:
        for r in resp["hits"]["hits"]:
            # print(r["_score"])
            img_src = r["_source"]["image_location"]
            static_source = "/static/siseveeb/" + "/".join(img_src.split("/")[2:])
            score_and_loc.append([r["_score"], static_source])

    score_and_loc.sort(key=lambda x: x[0], reverse=True)

    print(score_and_loc)
    response_html = [
        '<!DOCTYPE html>\n<html>  <head><title>Photos</title></head><body><h1>Photos</h1><div class="photo">'
    ]  # ".fit-picture {width: 250px;}"]
    ensure_unique = set()
    for _, loc in score_and_loc:
        template = f'<img class="fit-picture" src="{loc}"/>'
        if not template in ensure_unique:
            ensure_unique.add(template)
            response_html.append(template)

    response_html.append("</div>  </body></html>")
    return HTMLResponse(content="\n".join(response_html), status_code=200)


@app.get("/find")
def find_seltsivend_sarnased(first=str, last=str):

    resp = search_elastic_sarnased(first, last)

    face_vectors = []
    for doc in resp["hits"]["hits"]:
        face_vectors.append(doc["_source"]["face_vector"])

    print(f"Siseveebis oli {resp['hits']['total']['value']} aluspilti")

    resps = []
    for fv in face_vectors:
        resps.append(
            ESclient.search(
                index="unnamed",
                knn={
                    "field": "face_vector",
                    "query_vector": fv,
                    "k": 30,
                    "num_candidates": 200,
                },
                query={
                    "bool": {
                        "filter": {"term": {"version": "2"}},
                    },
                },
                source_includes=["gdrive_id"],
                source=False,
            )
        )
    print(f"Andmebaasist tuvastasime {len(resps)}")
    score_and_loc = []
    for resp in resps:
        print(resp)
        print("----------------------------------------------")
        for r in resp["hits"]["hits"]:
            # esimene if on deprecated
            if "image_location" in r["_source"]:
                img_src = r["_source"]["image_location"]
                static_source = "/static/" + "/".join(img_src.split("/")[2:])
                score_and_loc.append([r["_score"], static_source])
            elif "gdrive_id" in r["_source"]:
                gdrive = r["_source"]["gdrive_id"]
                static_source = f'<iframe src="https://drive.google.com/file/d/{gdrive}/preview" width="640" height="480"></iframe>'
                score_and_loc.append([r["_score"], static_source])
            else:
                print(r["_source"])

    score_and_loc.sort(key=lambda x: x[0], reverse=True)
    print(f"Andmebaasist tuvastasime {len(score_and_loc)}")
    print(score_and_loc)
    response_html = [
        f"""<!DOCTYPE html>\n<html>  <head><title>Photos</title></head><body><h1>Imelise {first} {last} pildid:</h1><div class="photo">"""
    ]
    ensure_unique = set()
    for _, loc in score_and_loc:
        if not loc in ensure_unique:
            ensure_unique.add(loc)
            response_html.append(loc)

    response_html.append("</div>  </body></html>")
    return HTMLResponse(content="\n".join(response_html), status_code=200)


@app.get("/create-unnamed")
def create_index_gdrive():
    ret = create_unnamed_index(ESclient)
    return {"message": f"{ret}"}


@app.get("/ingest-local")
def ingest_local():
    start = time.time()
    for asi in scan_unknown.directory_traversal(
        "./data/pildid/reduced/2024-l/Volber - Heino Pärn"
    ):
        print(asi)
        result = scan_unknown.process_image_multiple_faces(
            os.path.join(*asi)
        )  # face location within image, face chip, face vector
        if result != 0:
            for res in result:
                print(res[0], res[2][0])

                res2 = upload_unnamed_to_elastic(
                    ESclient,
                    index="unnamed",
                    face_vector=list(res[2]),
                    image_loc=os.path.join(*asi),
                    face_loc_img=res[0],
                    scale_factor=0.5,
                )
                print(res2)

    return {"message": f"Aega kulus: {time.time()-start} sekundit"}
