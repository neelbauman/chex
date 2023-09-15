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
    n_visited: int
    last: str


@dataclasses.dataclass
class Link:
    source: str
    target: str
    val: float
    n_passed: int
    last: str


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
        id_ = site["url"]
        name = site["url"]
        val = site["score"] + 1
        n_visited = site["n_visited"]
        last = site["last"]
        neighbors = site["hrefs"]

        node = asdict(Node(
            id_ = id_,
            name = name,
            val = val,
            n_visited = n_visited,
            last = last,
        ))
        data["nodes"].append(node)

        for href in site["hrefs"]:
            if href["url"] in node_list:
                source = site["url"]
                target = href["url"]
                val = href["score"] + 1
                n_passed = href["n_passed"]
                last = href["last"]

                link = asdict(Link(
                    source = source,
                    target = target,
                    val = val,
                    n_passed = n_passed,
                    last = last
                ))
                data["links"].append(link)
            else:
                pass
            
    return data


@app.get("/")
def index():
    file_path = "tmp/8b6a9f089f36cbef133e9b29438e6f04579181c4/index.json"
    data = load_json(file_path)
    data = make_input_json(data)
    return data


if __name__ == "__main__":
    data = index()
    print(data)
