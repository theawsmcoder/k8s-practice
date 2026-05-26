import os
from fastapi import FastAPI
from pydantic import BaseModel

import uvicorn

class Object(BaseModel):
    id: int
    name: str

app = FastAPI()

temp_data = {}

@app.get("/")
async def root():
    return {"app": os.getenv("APP_NAME")}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/config")
async def config():
    return {
        "db_host": os.getenv("DB_HOST"),
        "log_level": os.getenv("LOG_LEVEL"),
        "env": os.getenv("APP_ENV")
    }

@app.get("/secret")
async def secret():
    return {
        "db_password": os.getenv("DB_PASSWORD"),
        "api_key": os.getenv("API_KEY")
    }

@app.get("/crash")
async def crash():
    return os._exit(1)

@app.get("/objects")
async def get_all_objects():
    return temp_data

@app.get("/objects/{obj_id}")
async def get_object(obj_id: int):
    return {
        obj_id: str(temp_data[obj_id])
        }

@app.delete("/objects/{obj_id}")
async def get_object(obj_id: int):
    return temp_data.pop(obj_id) 

@app.post("/objects")
async def create_object(obj: Object):
    temp_data[obj.id] = obj.name
    return obj


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
