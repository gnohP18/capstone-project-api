import pandas as pd
from common import constant, functionHelper

class Seeder():
    def __init__(self) -> None:
        self.connect = "123"  
        
        
    def _documentSeeder(self) -> None:
        functionHelper.writeLog("_documentSeeder", constant.START_LOG)
        
        # TODO
        
        functionHelper.writeLog("_documentSeeder", constant.END_LOG)