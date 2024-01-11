from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.inventory import Inventory

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

inventory = Inventory("tts/testmath.json")

@app.get("/")
def index():
    data = inventory.asJSON()
    return data

def crawl():
    pass

if __name__ == "__main__":
    pass

