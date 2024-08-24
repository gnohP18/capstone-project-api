from pypdf import PdfReader, PdfWriter


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
