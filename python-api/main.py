from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import elasticsearch, document
from services import ModelSentence
from http import HTTPStatus
from common import returnMessage, functionHelper


##### API Constructor #####
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

model = ModelSentence()
# model.loadModel()


@app.get("/")
async def root():
    return {"message": "Xin chào, chào mừng bạn tới project của shubanoname"}


@app.get("/setup")
async def setup():
    print("====================> Initializing ...")
    model.loadModel()
    model.storageModel()
    print("====================> Done ...")
    return {
        "status_code": HTTPStatus.CREATED,
        "message": returnMessage.SETUP_MODEL_SUCCESS,
    }


@app.get("/reload")
async def reload():
    print("====================> Reloading ...")
    model.reloadModel()
    print("====================> Done ...")
    return {"status_code": HTTPStatus.OK, "message": returnMessage.RELOAD_MODEL_SUCCESS}


app.include_router(elasticsearch.router)
app.include_router(document.router)
