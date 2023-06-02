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

    result = connection.executeAndFetch(
        f'SELECT idAthlete FROM Athlete WHERE firstName = "Lene Berg" AND lastName = "AADLANDSVIK" AND nationAlpha3 = "NOR" AND birthday ="1993-01-09";')
    print(result)
