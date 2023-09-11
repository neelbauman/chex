from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import dataclasses
import json

app = FastAPI()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


def chg_key_name(fn):
    def fn_(*args, **kwargs):
        dict_data = fn(*args, **kwargs)
        data = {}
        for k in dict_data.keys():
            if k.endswith("_"):
                data[k[:-1]] = dict_data[k]
            else:
                data[k] = dict_data[k]

        return data

    return fn_

@chg_key_name
def asdict(data_obj) -> dict:
    return dataclasses.asdict(data_obj)


@dataclasses.dataclass
class Node:
    id_: str
    name: str
    val: float

@dataclasses.dataclass
class Link:
    source: str
    target: str


def load_json(file_path:str=""):
    with open(file_path, "r") as f:
        s = f.read()
    data = json.loads(s)
    return data

def make_input_json(index):
    data = {
        "nodes": [],
        "links": [],
    }

    node_list = [ site["url"] for site in index ]

    for i, site in enumerate(index):
        data["nodes"].append( asdict(Node(id_=site["url"],name=site["url"],val=1.0)) )
        for href in site["hrefs"]:
            if href["url"] in node_list:
                link = asdict(Link(source=site["url"],target=href["url"]))
                data["links"].append(link)
            else:
                pass
            
    return data

'''
@app.get("/")
def index():
    with open("tmp/index.json", "r") as f:
        s = f.read()
    data = json.loads(s)
    return data
'''

@app.get("/")
def index():
    file_path = "tmp/001.cycle.json"
    data = load_json(file_path)
    data = make_input_json(data)
    return data


if __name__ == "__main__":
    data = index()
    print(data)
