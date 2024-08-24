########## Header request ##########
HEADERS = {"Content-Type": "application/json"}

########## Body query ##########
MINIMUM_SHOULD_MATCH = 1

MINIMUM_WORD_SPLIT = 2

########## Conditional search ##########
ORDER_BY = {"ASC": "asc", "DESC": "desc"}

########## Batch size ##########
BATCH_SIZE_768 = 768

BATCH_SIZE_256 = 256

BATCH_SIZE_128 = 128

BATCH_SIZE_64 = 64

BATCH_SIZE_32 = 32

########## For test ##########
TEST_LIMIT_DATA = 100000

INDEX_TITLE_TEST = "title-data-test"

########## For model ##########
PHOBERT_BASE_PATH = "vinai/phobert-base"

TOKENIZER_PATH = "storage/tokenizer/"

MODEL_PATH = "storage/model/"

DIMS_768 = 768
DIMS_256 = 256
