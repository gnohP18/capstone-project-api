from typing import List
from pypdf import PdfReader, PdfWriter
from common import constant
from elasticsearch import Elasticsearch, helpers
from dtos import SearchConditionDto

def extractPageText(page) -> str:
    text = page.extract_text()
    combinedText = " ".join(text.split())
    return combinedText

def createObjectPage(reader, pageNumber) -> object:
    combinedText =  extractPageText(page=reader.pages[pageNumber])
    
    objectData = {
        "page_id": pageNumber,
        "words": combinedText,
        "page_number": pageNumber
    }
    
    return objectData

def readBookPdf(url: str) -> list:
    reader = PdfReader(url)
    
    # if file is encrypted, you must encrypt it!
    if reader.is_encrypted:
        writer = PdfWriter(clone_from=reader)
        with open(url, "wb") as f:
            writer.write(f)
            
    arrayObject = []
    
    for index in range(len(reader.pages)):
        arrayObject.append(createObjectPage(reader=reader, pageNumber=index))
    
    return arrayObject

def indexObjects(index: str, url: str):
    # create array index object
    arr = readBookPdf(url=url)
    
    # construct client
    esClient = Elasticsearch('http://elasticsearch:9200')
    
    # index bulk object
    helpers.bulk(esClient, arr, index=index)
    
def createObjectQuery(keyword: str, fields: List[str] = ["*"], optionMatch: str = "multi_match") -> object:
    # Boosting keyword follow the number of keyword
    # TODO: Handle keyword > 10 words
    boots = len(keyword.split())
    if boots > 2 :
        return {
            optionMatch: {
                "query": keyword,
                "fields": fields,
                "boost": boots
            } 
        }
    else :
        return {
            optionMatch: {
                "query": keyword,
                "fields": fields,
            } 
        }
    
def generateKeyword(keyword: str, miniumWord: int = constant.MINIMUM_WORD_SPLIT) -> List[str]:
    results = []
    words = keyword.split()
    for n in range(miniumWord, len(words) + 1):
        for i in range(len(words) - n + 1):
            combination = " ".join(words[i:i + n])
            results.append(combination)
    
    return results
    
def searching(dto: SearchConditionDto):
    esClient = Elasticsearch('http://elasticsearch:9200')
    objectQuery = []
    for keyword in dto.query:
        words = generateKeyword(keyword=keyword)
        for word in words:
            objectQuery.append(createObjectQuery(
                keyword=word, 
                fields=dto.fields, 
                optionMatch="multi_match"
            ))
            
    # Reverse array object
    objectQuery = objectQuery[::-1]
    
    print(objectQuery)       
    res = esClient.search(
        index=dto.index,
        body={
            "query": {
                "bool": {
                    "should": objectQuery,
                    "minimum_should_match": constant.MINIMUM_SHOULD_MATCH
                }
            },
            "sort": [
                {
                    "_score": {
                        "order": dto.orderBy
                    }
                }
            ],
            "size": dto.limit,
            "from": (dto.page - 1) * dto.limit
        }
    )
    
    return res