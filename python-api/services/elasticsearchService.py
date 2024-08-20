from typing import List
from pypdf import PdfReader, PdfWriter
from common import constant, functionHelper
from elasticsearch import Elasticsearch, helpers
from dtos import SearchConditionDto
from .sentenceService import ModelSentence
import pandas as pd
import os
model = ModelSentence()

elasticsearchUrl = os.environ["ELASTICSEARCH_HOSTS"]

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

def indexObjects(index: str, arrObject = []):    
    # construct client
    esClient = Elasticsearch(elasticsearchUrl)
    
    # index bulk object
    helpers.bulk(esClient, arrObject, index=index)
    
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
    '''
        Generate keyword follow miniumWord
    '''
    results = []
    words = keyword.split()
    for n in range(miniumWord, len(words) + 1):
        for i in range(len(words) - n + 1):
            combination = " ".join(words[i:i + n])
            results.append(combination)
    
    return results
    
def simpleSearch(dto: SearchConditionDto):
    '''
        Searching follow simple algorithm 
        Example: 
            "Tấm trèo cây" => generate keyword: "Tấm trèo", "trèo cây"
    '''
    esClient = Elasticsearch(elasticsearchUrl)
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
    
    return functionHelper.convertResourceSearch(data=res)

def createObjectTitle(docs):
    objects = []
    titleTokens = model.tokenizeArrayObject([item['title'] for item in docs])
    titleVectors = model.embeddingArrayObject(titleTokens)
    for i, doc in enumerate(docs):
        objectTitle = doc
        objectTitle["_op_type"] = "index"
        objectTitle["_index"] = "test"
        objectTitle["title_vector"] = titleVectors[i].tolist()
        objects.append(objectTitle)
    
    return objects
    
def createArrayTitleTestObject():
    df = pd.read_csv("./storage/data_title.csv")
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text"
                },
                "title_vector": {
                    "type": "dense_vector",
                    "dims": constant.BATCH_SIZE_768
                }
            }
        }
    }
    es_client = Elasticsearch(elasticsearchUrl)
    es_client.indices.create(index='test', body=mapping)
    total = df.shape[0]
    indexedCount = 0
    count = 0
    docs = []
    for index, row in df.iterrows():
        count += 1
        item = {
            'id': row['id'],
            'title': row['title']
        }
        docs.append(item)
        if count % constant.BATCH_SIZE_128 == 0:
            arrObject = createObjectTitle(docs)
            indexedCount += constant.BATCH_SIZE_128
            indexObjects(index="test-title", arrObject=arrObject)
            print(f"===========> Indexed {indexedCount}/{total}")
            docs = []
        if count > constant.TEST_LIMIT_DATA:
            docs = []
            break
    if docs:
        arrObject = createObjectTitle(docs)
        indexObjects(index="test-title", arrObject=arrObject)
        indexedCount += constant.BATCH_SIZE_128
        print(f"===========> Indexed {indexedCount}/{total}")
        
    
def semanticSearch(dto: SearchConditionDto):
    test = model.encodeSentence(dto.query[0])
    esClient = Elasticsearch(elasticsearchUrl)
    
    res = esClient.search(
        index=dto.index,
        body={ 
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {} 
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                        "params": {
                            "query_vector": test[0].tolist()
                        }
                    }
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
    
    return functionHelper.convertResourceSearch(data=res, field=["title"])
    
    
