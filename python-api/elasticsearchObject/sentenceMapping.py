from common import constant

class SentenceMapping():
    _map = {
        "mappings": {
            "properties": {
                "document_id": {"type": "keyword"},
                "page_number": {"type": "integer"},
                "sentence": {"type": "text"},
                "sentence_vector": {
                    "type": "dense_vector",
                    "dims": constant.DIMS_768,
                },
            }
        }
    }
