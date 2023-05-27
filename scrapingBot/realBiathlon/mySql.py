import mysql
import mysql.connector
import pandas as pd
import glob
import numpy as np
from functools import reduce
from mysql.connector.connection import MySQLConnection
from typing import Iterable, List, Tuple, Union
import csv
from realBiathlon.usefuls import tail


class mySqlObject:
    def __init__(self):
        self.db: MySQLConnection = mysql.connector.connect(
            user="root",
            password="R13251618a",
            host="127.0.0.1",)

        self.dbc = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.dbc.close()
        self.db.close()

    def useDatabase(self, dataBaseName: str) -> None:
        self.dbc.execute(f"USE {dataBaseName};")

    def executeCommand(self, command: str) -> None:
        self.dbc.execute(command)

    def executeAndCommit(self, command: str) -> None:
        self.dbc.execute(command)
        self.db.commit()

    def resetCursor(self) -> None:
        self.dbc.reset()

    def fetchResults(self):
        return self.dbc.fetchall()

    def insertFromCsv(self, csvPath: str, tableName: str, columnNames: Iterable[str], customCommand: Union[bool, str] = None) -> None:

        insertCommand = f"INSERT INTO {tableName} ({', '.join(columnNames)}) VALUES ({', '.join(['%s']*len(columnNames))})"

        rowLists: List[Tuple] = pd.read_csv(csvPath, keep_default_na=False, na_values=[
                                            'NULL', 'NAN', 'nan']).values.tolist()

        self.dbc.executemany(insertCommand, rowLists)

        self.db.commit()

        # self.executeCommand(insertCommand)
