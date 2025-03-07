import os
import json

# selleks et utilsist importida
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from utils import EShelper
from utils.EShelper import ESclient
from utils.EShelper import (
    search_elastic_by_name,
    search_elastic_similarity,
    create_named_index,
    upload_named_face_to_elastic,
    create_unnamed_index,
    upload_unnamed_to_elastic,
)

from utils import scan_known_faces_to_elastic, scan_unknown

from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends


# TODO remove before prod
import urllib3
import warnings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from elasticsearch.exceptions import ElasticsearchWarning

warnings.simplefilter("ignore", ElasticsearchWarning)


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(
        directory="/Users/toomas/Documents/Projects/naoraamat/backend/data/reduced"
    ),
    name="static",
)


origins = [
    "http://localhost:5173",
    "localhost:5173",
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


class VectorQuery(BaseModel):
    query_vector: List[float]


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


@app.get("/find")
def find_named(first: str, last: str):
    resp = search_elastic_by_name(first, last)
    clean = [r["_source"] for r in resp["hits"]["hits"]]
    print(f"Found {len(clean)} matches")
    return HTMLResponse(status_code=200, content=json.dumps(clean))


@app.post("/find_similar")
def find_similar(
    data: Optional[VectorQuery] = None,
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
):
    if data and (first_name or last_name):
        raise HTTPException(
            status_code=400,
            detail="Provide either a vector or name parameters, not both",
        )
    if data:  # If face_vector is provided
        fv = data.query_vector
        faces = ESclient.search(
            index="unnamed",
            knn={
                "field": "face_vector",
                "query_vector": fv,
                "k": 20,
                "num_candidates": 100,
            },
            # source_includes=["image_location"],
            # source=False,
        )
        clean = [c["hits"]["hits"] for c in faces]
        print(f"Found {len(clean)} matches")
        return HTMLResponse(status_code=200, content=clean)
    elif first_name and last_name:  # TODO not needed both names technically?
        named_response = find_named(first=first_name, last=last_name)
        # print(named_sources.content)
        named_sources = json.loads(named_response.body.decode())
        fvs = [ns["face_vector"] for ns in named_sources]
        resps = []
        print(f"Using {len(fvs)} facevectors as ground truth.")
        for fv in fvs:
            matches = ESclient.search(
                index="unnamed",
                knn={
                    "field": "face_vector",
                    "query_vector": fv,
                    "k": 20,
                    "num_candidates": 100,
                },
                # source_includes=["image_location", "first", "last"],
                # source=False,
            )
            resps.extend(matches["hits"]["hits"])
        # remove duplicates
        match_ids = set()
        new_resp = []
        for r in resps:
            if r["_id"] not in match_ids:
                match_ids.add(r["_id"])
                new_resp.append(r["_source"])
        print(f"Found {len(new_resp)} matches")
        return HTMLResponse(status_code=200, content=json.dumps(new_resp))

    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either a vector or both first_name and last_name",
        )


@app.get("/find_similar")
async def _find_similar(first: str, last: str):
    return find_similar(first_name=first, last_name=last)
