from typing import Any, Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Any]:
    # curl localhost:3000/items/1\?q=eee
    return {"item_id": item_id, "q": q}
