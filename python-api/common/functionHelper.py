from typing import List
from dotenv import load_dotenv
import os
import re
from common import constant


def loadEnvironment(env: str = constant.LOCAL_ENV):
    envDir = "./.env"
    if env != constant.LOCAL_ENV:
        envDir = "./.env." + env
    load_dotenv(envDir)
    return os.environ


def convertResourceSearch(data, field: List[str] = ["*"]) -> List[object]:
    sources = [hit["_source"] for hit in data["hits"]["hits"]]
    dataReturn = []
    if field[0] == "*":
        for item in sources:
            dataReturn.append(item["_source"])
    else:
        for item in sources:
            nestedItem = {}

            for key in field:
                if key in item:
                    nestedItem[key] = item[key]

            dataReturn.append(nestedItem)

    return dataReturn


def generateUrlStorage(name: str = "", env: str = constant.LOCAL_ENV):
    if name == "":
        return
    envVariable = loadEnvironment()

    # Check if local
    if env == constant.LOCAL_ENV:
        # Check if storage path is exist
        if not os.path.exists(envVariable["LOCAL_DIR"]):
            print("==========> Path is not exist, create a new path")
            os.makedirs(envVariable["LOCAL_DIR"])

        return os.path.join(envVariable["LOCAL_DIR"], name)

    # if not local -> handle AWS or another service
    # TODO


def generateUrlPreview(names: List[str] = []) -> List[str]:
    # query to get list path
    # check if type is in another service like AWS 
    
    return ["storage/documents/Topics_1_2_20240824_050225.pdf"]

def writeLog(param: str = "", type: str = constant.START_LOG):
    print(f"==================={type} - {param}===================>")
    

def standardizationText(sentences):
    sentences = sentences.replace('  ', ' ');
    
    return re.sub(constant.PATTERN, ' ', sentences).lower()