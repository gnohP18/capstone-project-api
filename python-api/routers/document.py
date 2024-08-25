from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import services
from common import returnMessage
from http import HTTPStatus
from services import DocumentService

router = APIRouter(prefix="/document")


@router.get("/")
async def get(name: str) -> str:
    testUrl2 = "./book/dac-nhan-tam.pdf"
    arr = services.elasticsearchService.readBookPdf(url=testUrl2)
    
@router.post("/upload")
async def uploadDocument(file: UploadFile = File()):
    print("==========> Upload file")
    DocumentService.uploadDocumentService(file=file)
    
    return {"message": returnMessage.SEARCH_SUCCESS, "code": HTTPStatus.OK}

@router.get("/preview")
async def previewDocument(name: str):
    path = DocumentService.previewDocumentService(name)
    
    return FileResponse(path, media_type="application/pdf", headers={"Content-Disposition": "inline"})
    