import mysql.connector
from common import functionHelper, constant

class DatabaseSetup:
    def __init__(self) -> None:
        """
            Load config from .env
        """        
        self.configDataBase = functionHelper.loadEnvironment(constant.LOCAL_ENV)
        
        self.connectorDB = mysql.connector.connect(
            host=self.configDataBase["DB_HOST"],
            user=self.configDataBase["DB_USERNAME"],
            password=self.configDataBase["DB_PASSWORD"],
            database=self.configDataBase["DB_DATABASE"],
        )
        
    def __setupDatabase__(self) -> None:
        functionHelper.writeLog("__setupDatabase__", constant.START_LOG)
        
        executeMysql = self.connectorDB.cursor(buffered=True)
                
        """
            Create documents table
        """
        executeMysql.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id CHAR(36) PRIMARY KEY, -- UUID stored as a 36-character string
                name NVARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            """
        )
        
        """
            Create media_files table
        """
        executeMysql.execute(
            """
            CREATE TABLE IF NOT EXISTS media_files (
                id CHAR(36) PRIMARY KEY, -- UUID stored as a 36-character string
                document_id CHAR(36), -- Ensure this matches the type of 'id' in document table
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES document(id)
            );
            """
        )
        
        """
            Create sentences table
        """
        executeMysql.execute(
            """
            CREATE TABLE IF NOT EXISTS sentences (
                id CHAR(36) PRIMARY KEY, -- UUID stored as a 36-character string
                document_id CHAR(36), -- Ensure this matches the type of 'id' in document table
                sentence NVARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES document(id)
            );
            """
        )
        
        functionHelper.writeLog("__setupDatabase__", constant.END_LOG)
        