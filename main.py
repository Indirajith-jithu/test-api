from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Simple CRUD API", version="1.0.0")

# --- In-memory "database" ---
db: dict[int, dict] = {}
counter: int = 0


# --- Schemas ---
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class Item(ItemCreate):
    id: int


# --- Routes ---

@app.get("/")
def root():
    return {"message": "Welcome to Simple CRUD API 🚀"}


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    global counter
    counter += 1
    new_item = {"id": counter, **item.model_dump()}
    db[counter] = new_item
    return new_item


@app.get("/items", response_model=list[Item])
def list_items():
    return list(db.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updates: ItemUpdate):
    item = db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        item[field] = value
    db[item_id] = item
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    del db[item_id]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)