from typing import List
from common import constant, functionHelper
from elasticsearch import Elasticsearch, helpers
from dtos import SearchConditionDto, SentenceDto, DocumentDto
from elasticsearchObject import DocumentMapping
from .sentenceService import ModelSentence
from http import HTTPStatus
import pandas as pd
from datetime import datetime, time
import json
import os


class ElasticsearchService:
    def __init__(self) -> None:
        self.elasticsearchUrl = os.getenv(
            "ELASTICSEARCH_HOSTS", "http://elasticsearch:9200/"
        )
        self.BATCH_SIZE = os.getenv("BATCH_SIZE", constant.BATCH_SIZE_256)
        self.esClient = Elasticsearch(self.elasticsearchUrl)
        self.model = ModelSentence()

    def indexObjects(self, index: str, arrObject=[]):
        # index bulk object
        resp = helpers.bulk(self.esClient, arrObject, index=index)
        # Print object resp

    def createObjectQuery(
        keyword: str, fields: List[str] = ["*"], optionMatch: str = "multi_match"
    ) -> object:
        # Boosting keyword follow the number of keyword
        # TODO: Handle keyword > 10 words
        boots = len(keyword.split())
        if boots > 2:
            return {optionMatch: {"query": keyword, "fields": fields, "boost": boots}}
        else:
            return {
                optionMatch: {
                    "query": keyword,
                    "fields": fields,
                }
            }

    def generateKeyword(
        keyword: str, miniumWord: int = constant.MINIMUM_WORD_SPLIT
    ) -> List[str]:
        """
        Generate keyword follow miniumWord
        """
        results = []
        words = keyword.split()
        for n in range(miniumWord, len(words) + 1):
            for i in range(len(words) - n + 1):
                combination = " ".join(words[i : i + n])
                results.append(combination)

        return results

    def simpleSearch(self, dto: SearchConditionDto):
        """
        Searching follow simple algorithm
        Example:
            "Tấm trèo cây" => generate keyword: "Tấm trèo", "trèo cây"
        """

        objectQuery = []
        for keyword in dto.query:
            words = self.generateKeyword(keyword=keyword)
            for word in words:
                objectQuery.append(
                    self.createObjectQuery(
                        keyword=word, fields=dto.fields, optionMatch="multi_match"
                    )
                )

        # Reverse array object
        objectQuery = objectQuery[::-1]

        res = self.esClient.search(
            index=dto.index,
            body={
                "query": {
                    "bool": {
                        "should": objectQuery,
                        "minimum_should_match": constant.MINIMUM_SHOULD_MATCH,
                    }
                },
                "sort": [{"_score": {"order": dto.orderBy}}],
                "size": dto.limit,
                "from": (dto.page - 1) * dto.limit,
            },
        )

        return functionHelper.convertResourceSearch(data=res)

    def createObjectTitle(self, docs):
        objects = []
        titleTokens = self.model.tokenizeArrayObject([item["title"] for item in docs])
        titleVectors = self.model.embeddingArrayObject(titleTokens)
        for i, doc in enumerate(docs):
            objectTitle = doc
            objectTitle["_op_type"] = "index"
            objectTitle["_index"] = "test"
            objectTitle["title_vector"] = titleVectors[i].tolist()
            objects.append(objectTitle)

        return objects

    def createArrayTitleTestObject(self):
        df = pd.read_csv("./storage/data_title.csv")
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "title_vector": {"type": "dense_vector", "dims": constant.DIMS_768},
                }
            }
        }

        self.esClient.indices.create(index="test", body=mapping)
        total = df.shape[0]
        indexedCount = 0
        count = 0
        start = datetime.now
        docs = []
        for index, row in df.iterrows():
            count += 1
            item = {"id": row["id"], "title": row["title"]}
            docs.append(item)
            if count % self.BATCH_SIZE_128 == 0:
                arrObject = self.createObjectTitle(docs)
                self.indexObjects(index=constant.INDEX_TITLE_TEST, arrObject=arrObject)

                indexedCount += self.BATCH_SIZE_128

                print(f"===========> Indexed {indexedCount}/{total}")
                docs = []
            if count > constant.TEST_LIMIT_DATA:
                docs = []
                break
        if docs:
            arrObject = self.createObjectTitle(docs)
            self.indexObjects(index=constant.INDEX_TITLE_TEST, arrObject=arrObject)
            indexedCount += self.BATCH_SIZE_128

            print(f"===========> Indexed {indexedCount}/{total}")

        end = datetime.timedelta(time.time() - start)

        print(f"===========> Done indexed {count}/{total} in {end}")

    def semanticSearch(self, dto: SearchConditionDto):
        embeddingSentence = self.model.encodeSentence(dto.query[0])
        sourceQuery = (
            "cosineSimilarity(params.query_vector, '" + dto.fieldVector + "') + 1.0"
        )

        res = self.esClient.search(
            index=dto.index,
            body={
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": sourceQuery,
                            "params": {"query_vector": embeddingSentence[0].tolist()},
                        },
                    }
                },
                "sort": [{"_score": {"order": dto.orderBy}}],
                "size": dto.limit,
                "from": (dto.page - 1) * dto.limit,
            },
        )

        # arr = functionHelper.convertResourceSearch(data=res, field=["sentence"])
        return res

    def documentObjectIndex(self, documentDto: DocumentDto):
        try:
            ##### Document #####
            # Handle create mapping for document
            # Embedding name
            embeddingName = self.model.encodeSentence(documentDto.name)

            isExistIndex = self.esClient.indices.exists(index=constant.INDEX_TEST_FILE)

            # check if index is exist
            if isExistIndex is False:
                # if not create new index
                self.esClient.indices.create(
                    index=constant.INDEX_TEST_FILE, body=DocumentMapping._map
                )

            # Mapping DocumentDto with DocumentObject
            documentObject = {
                "_op_type": "index",
                "_index": constant.INDEX_TEST_FILE,
                "id": documentDto.id,
                "name": documentDto.name,
                "number_of_page": documentDto.number_of_page,
                "type_doc": documentDto.type_doc,
                "name_vector": embeddingName[0].tolist(),
            }

            self.indexObjects(
                index=constant.INDEX_TEST_FILE, arrObject=[documentObject]
            )
        except Exception as e:
            print(str(e))
            return {"error": str(e)}

    def createSentenceObject(
        self,
        index: str,
        arrSentenceDto: List[SentenceDto],
        embeddingKey: str = "sentence",
        vectorKey: str = "vector",
        opType: str = "index",
    ):
        objects = []

        sentenceTokens = self.model.tokenizeArrayObject(
            arr=[item.__getField__(embeddingKey) for item in arrSentenceDto]
        )
        sentenceVectors = self.model.embeddingArrayObject(sentenceTokens)

        for i, doc in enumerate(arrSentenceDto):
            sentenceObject = {
                "_op_type": opType,
                "_index": index,
                "id:": doc.id,
                "document_id:": doc.document_id,
                "page_number:": doc.page_number,
                "sentence:": doc.sentence,
                vectorKey: sentenceVectors[i].tolist(),
            }

            objects.append(sentenceObject)

        return objects

    def sentenceObjectIndex(self, fileName: str, arrSentenceDto: List[SentenceDto]):
        try:
            ##### Sentence #####
            # count record and sent it to batch
            total = len(arrSentenceDto)
            count = 0
            indexedCount = 0
            start = datetime.now
            docs = []

            # iterate record in array
            for sentence in arrSentenceDto:
                count += 1
                docs.append(sentence)

                if count % self.BATCH_SIZE == 0:
                    arrObject = self.createSentenceObject(
                        index=fileName,
                        embeddingKey="sentence",
                        vectorKey="sentence_vector",
                        arrSentenceDto=docs,
                        opType="index",
                    )

                    self.indexObjects(index=fileName, arrObject=arrObject)

                    indexedCount += self.BATCH_SIZE

                    print(f"===========> Indexed {indexedCount}/{total}")
                    docs = []
                if count > constant.TEST_LIMIT_DATA:
                    docs = []
                    break
            if docs:
                arrObject = self.createSentenceObject(
                    index=fileName,
                    embeddingKey="sentence",
                    vectorKey="sentence_vector",
                    arrSentenceDto=docs,
                    opType="index",
                )
                self.indexObjects(index=fileName, arrObject=arrObject)
                indexedCount += self.BATCH_SIZE

                print(f"===========> Indexed {indexedCount}/{total}")

            # count time
            end = datetime.fromtimestamp(datetime.now - start)

            # count record
            print(f"===========> Done indexed {count}/{total} in {end}")

        except Exception as e:
            print(str(e))
            return {"error": str(e)}
