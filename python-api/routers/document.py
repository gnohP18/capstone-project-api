from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form
from fastapi.responses import FileResponse
import services
from common import returnMessage, functionHelper, constant
from http import HTTPStatus
from services import DocumentService
import os

router = APIRouter(prefix="/document")
documentService = DocumentService()

@router.get("/")
async def get(name: str) -> str:
    testUrl2 = "./book/dac-nhan-tam.pdf"
    arr = services.elasticsearchService.readBookPdf(url=testUrl2)
    
@router.post("/upload")
async def uploadDocument(
    name: str = Form(...),
    type: str = Form(...),
    is_embedding: str = Form(...), 
    file: UploadFile = File(...)):
    
    functionHelper.writeLog(uploadDocument.__name__, constant.START_LOG)
    
    fileName, fileExtension = os.path.splitext(file.filename)
    if fileExtension not in constant.ALLOW_EXT:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Extension is not allowed")
    
    is_embedding = is_embedding.lower() == "true"
    
    documentService.uploadDocumentService(name=name, type=type, file=file, isEmbedding=is_embedding)
    
    functionHelper.writeLog(uploadDocument.__name__, constant.END_LOG)
    return {"message": returnMessage.UPLOAD_FILE_SUCCESS, "code": HTTPStatus.OK}

@router.get("/preview")
async def previewDocument(name: str):
    functionHelper.writeLog(previewDocument.__name__, constant.START_LOG)
    
    path = DocumentService.previewDocumentService(name)
    
    functionHelper.writeLog(previewDocument.__name__, constant.END_LOG)
    
    return FileResponse(path, media_type="application/pdf", headers={"Content-Disposition": "inline"})
    