from fastapi import APIRouter
import services
from dtos import SearchConditionDto
from http import HTTPStatus
router = APIRouter(prefix="/es")

@router.post("/index-object")
async def makeIndex(index: str):
    testUrl1 = "./book/tam-cam.pdf"
    testUrl2 = "./book/dac-nhan-tam.pdf"
    testUrl3 = "./book/thanh-sanh-ly-thong.pdf"
    services.elasticsearchService.indexObjects(index=index, url=testUrl2)
    
    return HTTPStatus.OK

@router.post("/search")
async def search(dto: SearchConditionDto):
    res = services.elasticsearchService.searching(dto=dto)
    return res