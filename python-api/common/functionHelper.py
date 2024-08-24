from typing import List
from dotenv import load_dotenv
import os


def loadEnvironment():
    # Lấy giá trị môi trường (environment) từ biến ENV
    env = os.getenv("ENV", "local")  # Nếu không có ENV, mặc định là 'local'

    # Chọn tệp .env tương ứng
    if env == "local":
        load_dotenv(".env.local")
    elif env == "dev":
        load_dotenv(".env.dev")
    else:
        raise ValueError(f"Unknown environment: {env}")


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
