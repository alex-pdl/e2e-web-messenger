import sqlite3

class Table:
    def __init__(self,database,table_name):
        self.database = database
        self.table_name = table_name
        self.connection = sqlite3.connect(f"{self.database}.db")
        self.cursor = self.connection.cursor()

    def create(self,col_1,col_2,col_3):
        create = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
            {col_1} INTEGER PRIMARY KEY NOT NULL,
            {col_2} INTEGER,
            {col_3} INTEGER
        ) """
        self.cursor.execute(create)
        self.connection.close()

class Users(Table):
    def __init__(self,database,table_name,username,password,public_key):
        super().__init__(database,table_name,connection)
        self.username = username
        self.password = password
        self.public_key = public_key