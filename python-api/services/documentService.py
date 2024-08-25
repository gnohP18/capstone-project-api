from pypdf import PdfReader, PdfWriter
from common import functionHelper
from fastapi import File, UploadFile
import shutil
from datetime import datetime
import os


class DocumentService:
    def extractPageText(page) -> str:
        text = page.extract_text()
        combinedText = " ".join(text.split())
        return combinedText

    def createObjectPage(self, reader, pageNumber) -> object:
        combinedText = self.extractPageText(page=reader.pages[pageNumber])

        objectData = {
            "page_id": pageNumber,
            "words": combinedText,
            "page_number": pageNumber,
        }

        return objectData

    def readBookPdf(self, url: str) -> list:
        reader = PdfReader(url)

        # if file is encrypted, you must encrypt it!
        if reader.is_encrypted:
            writer = PdfWriter(clone_from=reader)
            with open(url, "wb") as f:
                writer.write(f)

        arrayObject = []

        for index in range(len(reader.pages)):
            arrayObject.append(self.createObjectPage(reader=reader, pageNumber=index))

        return arrayObject

    def previewDocumentService(name: str):
        if name == "":
            return

        url = functionHelper.generateUrlPreview([name])
        
        return url[0]

    def uploadDocumentService(file: UploadFile = File()):
        try:
            currentTime = datetime.now().strftime("%Y%m%d_%H%M%S")
            fileName, fileExtension = os.path.splitext(file.filename)
            fullFileName = fileName + "_" + currentTime + fileExtension
            dirFile = functionHelper.generateUrlStorage(name=fullFileName)
            # Handle create object Media
            
            with open(dirFile, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Handle read document if need
        
        except Exception as e:
            return {"error": str(e)}