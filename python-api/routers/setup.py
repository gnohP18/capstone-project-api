from fastapi import APIRouter
from common import returnMessage
from http import HTTPStatus
from database.databaseSetup import DatabaseSetup
from services import ModelSentence
from common import functionHelper, constant

router = APIRouter(prefix="/setup")

db = DatabaseSetup()

@router.get("/model")
async def setupModel() -> dict[str, str]:
    """
        Setup model - call when have issue with networking
    """
    functionHelper.writeLog("setupModel", constant.START_LOG)
    
    model = ModelSentence()
    model.__loadModel__()
    # model.storageModel()

    functionHelper.writeLog("setupModel", constant.START_LOG)

    return {
        "status_code": HTTPStatus.CREATED,
        "message": returnMessage.SETUP_MODEL_SUCCESS,
    }
    
    
@router.get("/database")
async def setupDatabase() -> dict[str, str]:
    functionHelper.writeLog(setupDatabase.__name__, constant.START_LOG)

    db = DatabaseSetup()
    db.__setupDatabase__()

    functionHelper.writeLog(setupDatabase.__name__, constant.END_LOG)

    return {
        "status_code": HTTPStatus.CREATED,
        "message": returnMessage.SETUP_DATABASE_SUCCESS,
    }


@router.get("/model-reload")
async def reloadModel() -> dict[str, str]:
    functionHelper.writeLog("reloadModel", constant.START_LOG)
    
    model = ModelSentence()
    model.reloadModel()
    
    functionHelper.writeLog("reloadModel", constant.END_LOG)
    
    return {"status_code": HTTPStatus.OK, "message": returnMessage.RELOAD_MODEL_SUCCESS}