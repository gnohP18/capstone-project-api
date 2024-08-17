from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import elasticsearch
import uuid

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": uuid.uuid4()}

app.include_router(elasticsearch.router) 