from fastapi import APIRouter
from services import ElasticsearchService
from dtos import SearchConditionDto
from common import returnMessage
from http import HTTPStatus

router = APIRouter(prefix="/es")

elasticsearchService = ElasticsearchService()

@router.post("/index-object")
async def makeIndex(index: str):
    testUrl1 = "./book/tam-cam.pdf"
    testUrl2 = "./book/dac-nhan-tam.pdf"
    testUrl3 = "./book/thanh-sanh-ly-thong.pdf"
    arr = elasticsearchService.readBookPdf(url=testUrl2)
    elasticsearchService.indexObjects(index=index, arrObject=arr)

    return {"message": returnMessage.CREATE_SUCCESS, "code": HTTPStatus.OK, "data": []}


@router.post("/index-title-data")
async def makeIndexTitle():
    elasticsearchService.createArrayTitleTestObject()

    return {"message": returnMessage.CREATE_SUCCESS, "code": HTTPStatus.OK, "data": []}


@router.post("/simple-search")
async def search(dto: SearchConditionDto):
    res = elasticsearchService.simpleSearch(dto=dto)

    return {"message": returnMessage.SEARCH_SUCCESS, "code": HTTPStatus.OK, "data": res}


@router.post("/semantic-search")
async def semanticSearch(dto: SearchConditionDto):
    res = elasticsearchService.semanticSearch(dto=dto)

    return {"message": returnMessage.SEARCH_SUCCESS, "code": HTTPStatus.OK, "data": res}
