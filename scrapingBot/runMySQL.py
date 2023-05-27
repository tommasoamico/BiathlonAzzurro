from realBiathlon.mySql import mySqlObject
from pprint import pprint
from realBiathlon.usefuls import getCsvHeader
from typing import List
import pandas as pd
import numpy as np

pathCsv: str = '/Users/tommaso/Workspace/BiathlonAzzurro/data/scrapingBot/newAthletesTable.csv'
tableName: str = 'Athlete'
columnNames: List[str] = ['firstName', 'lastName',
                          'birthday', 'nationAlpha3', 'gender', 'idNation']


customCommand = f"""INSERT INTO {tableName} ({', '.join(columnNames)})
VALUES ()
"""

with mySqlObject() as connection:

    connection.useDatabase('biathlon')

    for row in pd.read_csv(pathCsv).values.tolist():
        if isinstance(row[2], float):
            command = f"""INSERT INTO {tableName} ({', '.join(columnNames)})
        VALUES ("{row[0]}","{row[1]}",NULL,(SELECT alpha3 FROM nation WHERE alpha2 = '{row[3]}'), '{row[4]}', (SELECT idNation FROM nation n WHERE n.alpha2 = '{row[3]}'))"""
        else:
            command = f"""INSERT INTO {tableName} ({', '.join(columnNames)})
        VALUES ("{row[0]}","{row[1]}",'{row[2]}',(SELECT alpha3 FROM nation WHERE alpha2 = '{row[3]}'), '{row[4]}', (SELECT idNation FROM nation n WHERE n.alpha2 = '{row[3]}'))"""
        connection.executeAndCommit(command)
