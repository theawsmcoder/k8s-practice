import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, select, Field
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
import uvicorn


secrets_dir = "/etc/secrets/"
secrets_dict = {}

for file_name in os.listdir(secrets_dir):
    path = os.path.join(secrets_dir, file_name)
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            secrets_dict[file_name] = f.read().strip()

print(secrets_dict)

# create a simple base model 
class ObjectBase(SQLModel):
    name: str

# create a database schema out of the above model
class Object(ObjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# create an engine to interact with the db
# print("USER DEBUG: " + os.getenv("POSTGRES_URL"))
# print("USER DEBUG: " + secrets_dict["POSTGRES_URL"])
engine = create_async_engine(secrets_dict["POSTGRES_URL"])

# yield a separate session for each query
async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as sess:
        yield sess

@asynccontextmanager
async def lifespan(app: FastAPI):
    # things to do before app initializes
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield
    # things to do before closing the app
    await engine.dispose()

app = FastAPI(title=os.getenv("APP_NAME"), lifespan=lifespan)

@app.get("/")
async def root():
    return {"app": os.getenv("APP_NAME")}

# for health check 
@app.get("/health")
async def health():
    return {"status": "ok"}

# for configmaps
@app.get("/config")
async def config():
    return {
        "db_host": os.getenv("POSTGRES_USER"),
        "log_level": os.getenv("LOG_LEVEL"),
        "env": os.getenv("APP_ENV")
    }

# for secrets
@app.get("/secret")
async def secret():
    return {
        "db_password": secrets_dict["POSTGRES_PASSWORD"],
        "api_key": secrets_dict["API_KEY"]
    }

# to intentionally crash the pod
@app.get("/crash")
async def crash():
    os._exit(1)

# to test storage related stuff
@app.get("/objects")
async def get_all_objects(db_session: AsyncSession = Depends(get_session)):
    results = await db_session.exec(select(Object))
    return results.all()

@app.get("/objects/{obj_id}")
async def get_object(obj_id: int, db_session: AsyncSession = Depends(get_session)):
    result = await db_session.get(Object, obj_id)
    if not result:
        raise HTTPException(status_code=404, detail="object not found")
    return result

@app.delete("/objects/{obj_id}")
async def delete_object(obj_id: int, db_session: AsyncSession = Depends(get_session)):
    temp = await db_session.get(Object, obj_id)
    if not temp:
        raise HTTPException(status_code=404, detail="object not found")
    await db_session.delete(temp)
    await db_session.commit()
    return {"deleted": obj_id}

@app.post("/objects")
async def create_object(obj: Object, db_session: AsyncSession = Depends(get_session)):
    temp = Object(name=obj.name)
    db_session.add(temp)
    await db_session.commit()
    await db_session.refresh(temp)
    return temp

if __name__ == "__main__":
    print(secrets_dict)
    uvicorn.run(app, host="0.0.0.0", port=8080)
