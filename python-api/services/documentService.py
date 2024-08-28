from typing import List

import unidecode
import PyPDF2
from common import functionHelper, constant
from fastapi import File, UploadFile, HTTPException
from http import HTTPStatus
from elasticsearch import Elasticsearch
from elasticsearchObject import SentenceMapping
from .elasticsearchService import ElasticsearchService
import shutil
from datetime import datetime
import os
from dtos import SentenceDto, DocumentDto
import uuid


class DocumentService:
    def __init__(self) -> None:
        self.elasticsearchUrl = os.getenv(
            "ELASTICSEARCH_HOSTS", "http://elasticsearch:9200/"
        )
        self.BATCH_SIZE = os.getenv("BATCH_SIZE", constant.BATCH_SIZE_256)
        self.elasticsearchService = ElasticsearchService()

    def _extractPageText(
        self, text: str, wordPerChunk: int = constant.MAX_LENGTH_SENTENCE
    ) -> List[str]:
        """extract text from page if text is name of document, we don't need.
        We need a custom split sentence to increase accuracy each sentence

        Args:
            text (str): text from page extract by PyPDF2
            wordPerChunk (int, optional): split by average of Vietnamese sentence.
            Defaults to constant.MAX_LENGTH_SENTENCE.

        Returns:
            List[str]: List string result
        """
        # sentences = re.split(r'(?<=\.)\s+', text)
        # return sentences

        words = text.split()
        splitText = []

        for i in range(0, len(words), wordPerChunk):
            chunk = " ".join(words[i : i + wordPerChunk])
            splitText.append(chunk)
        return splitText

    def _generateIndexFromName(self, fileName: str) -> str:
        """generate index from name
        lowercase name -> remove special character and split it
        Need solve case have special in character

        Args:
            fileName (str): Ex: Biên bản bàn giao tài sản, 01. MCS0004_Biên bản bàn giao tài sản

        Returns:
            name: indexname
        """
        fileName = unidecode.unidecode(fileName)
        standardText = functionHelper.standardizationText(fileName)
        words = standardText.split()

        return "_".join(words)

    def _createObjectPage(
        self, pageNumber: int, bookId: str, sentenceArr: List[str] = []
    ) -> List[SentenceDto]:
        """Create list object sentenceDto follow parameters

        Args:
            pageNumber (int): number of page
            bookId (str): Book_id follow database
            sentenceArr (List[str], optional): List string from _extractPageText. Defaults to [].

        Returns:
            List[SentenceDto]: _description_
        """
        sentenceDtoArr: List[SentenceDto] = []

        for sentence in sentenceArr:
            sentenceDto = SentenceDto(
                id=str(uuid.uuid4()),
                document_id=str(bookId),
                page_number=pageNumber,
                sentence=sentence,
            )

            sentenceDtoArr.append(sentenceDto)

        return sentenceDtoArr

    def _readDocument(
        self, name: str, fileName: str, typeDoc: str, url: str
    ) -> tuple[list[SentenceDto], DocumentDto]:
        """Read document from url. Encrypt document. Create array SentenceDto and DocumentDto

        Args:
            name (str): Such as description of the document
            fileName (str): filename
            typeDoc (str):  type of document like: Biên bản, chứng từ, ...
            url (str): Link of url

        Returns:
            tuple[list[SentenceDto], DocumentDto]: Result
        """
        try:
            # PyPDF2 read pdf
            reader = PyPDF2.PdfReader(url)

            # if file is encrypted, you must decrypt it!
            # copy decrypt to anther file
            if reader.is_encrypted:
                writer = PyPDF2.PdfWriter(clone_from=reader)
                with open(url, "wb") as f:
                    writer.write(f)

            arrayObject: List[SentenceDto] = []
            bookId = uuid.uuid4()
            count = 0

            for page in reader.pages:
                # lower text and remove special characters
                standardizeText = functionHelper.standardizationText(
                    page.extract_text()
                )

                # split text by dot(.)
                fullText = self._extractPageText(
                    text=standardizeText, wordPerChunk=constant.MAX_LENGTH_SENTENCE
                )
                arrayObject = arrayObject + self._createObjectPage(
                    pageNumber=count, bookId=bookId, sentenceArr=fullText
                )
                count += 1

            documentDto = DocumentDto(
                id=str(bookId),
                name=name,
                file_name=fileName,
                number_of_page=count,
                type_doc=typeDoc,
            )

            return arrayObject, documentDto
        except Exception as e:
            return {"error": str(e)}

    def previewDocumentService(name: str):
        if name == "":
            return

        url = functionHelper.generateUrlPreview([name])

        return url[0]

    def uploadDocumentService(
        self, name: str, type: str, file: UploadFile = File(), isEmbedding: bool = False
    ):
        try:
            currentTime = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Get filename, extension file ex: pdf, doc
            fileName, fileExtension = os.path.splitext(file.filename)

            fullFileName = fileName + "_" + currentTime + fileExtension
            dirFile = functionHelper.generateUrlStorage(name=fullFileName)

            # Handle create object Media
            # TODO

            with open(dirFile, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            if isEmbedding is True:
                # generate index depends on file name
                indexFileName = self._generateIndexFromName(name)

                # check index from generate index
                esClient = Elasticsearch(self.elasticsearchUrl)

                # Check if exist index
                isExistIndex = esClient.indices.exists(index=indexFileName)

                if isExistIndex == False:
                    # Create mapping for sentence
                    reps = esClient.indices.create(
                        index=indexFileName, body=SentenceMapping._map
                    )
                    if reps["acknowledged"] == True:
                        print(f"===========> create new index {fileName}")
                else:
                    raise HTTPException(
                        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                        detail="Extension is not allowed",
                    )

                # Handle read document if need
                # Handle create array object SentenceDto
                arrSentence, document = self._readDocument(
                    name=name, fileName=fullFileName, typeDoc=fileExtension, url=dirFile
                )

                # Handle create Object elasticsearch

                self.elasticsearchService.documentObjectIndex(documentDto=document)

                self.elasticsearchService.sentenceObjectIndex(
                    fileName=indexFileName, arrSentenceDto=arrSentence
                )

        except Exception as e:
            return {"error": str(e)}
