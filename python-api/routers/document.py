from fastapi import APIRouter
import services
from common import returnMessage
from http import HTTPStatus

router = APIRouter(prefix="/document")


@router.get("/")
async def get(name: str) -> str:
    testUrl2 = "./book/dac-nhan-tam.pdf"
    arr = services.elasticsearchService.readBookPdf(url=testUrl2)
