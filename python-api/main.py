from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import elasticsearch, document, setup
from services import ModelSentence
from common import functionHelper


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
##### Load config #####
env = functionHelper.loadEnvironment()

##### Load model #####
model = ModelSentence()
if env["LOAD_MODEL"] == 'True':
    model.__loadModel__()

@app.get("/")
async def root():    
    return {"message": "Xin chào, chào mừng bạn tới project của shubanoname"}

app.include_router(setup.router)
app.include_router(elasticsearch.router)
app.include_router(document.router)
