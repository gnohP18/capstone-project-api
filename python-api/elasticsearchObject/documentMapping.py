from common import constant
    
class DocumentMapping():
    _map = {
        "mappings": {
            "properties": {
                "name": {"type": "text"},
                "number_of_page": {"type": "integer"},
                "type_doc": {"type": "text"},
                "name_vector": {"type": "dense_vector", "dims": constant.DIMS_768},
            }
        }
    }