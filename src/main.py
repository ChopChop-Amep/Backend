__version__ = "0.1.0"

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root():
    return {"Hello": "World", "Programmed": "To work", "But not": "To feel"}
