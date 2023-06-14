from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Union, Tuple
import pandas as pd
from pprint import pprint
from realBiathlon.constants import specialCases
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from realBiathlon.mySql import mySqlObject
from typing import Type
from realBiathlon.loopTimes import getLoopTimes


class retrieveRaceResults:
    allInstances: List[Type] = []

    def __init__(self, driver: WebDriver, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId
        self.allInstances.append(self)

    def __findBirthday(self) -> List[str]:
        divBirthday: WebElement = self.drvr.find_element(
            By.ID, 'pagesubheaderright')
        birthday: List[str] = re.findall(
            r'\d{4}-\d{2}-\d{2}', divBirthday.text)
        return birthday

    @staticmethod
    def __idQuery(firstName: str, lastName: str, nation: str, birthday: str) -> int:
        assert len(
            nation) == 3, "Nation in the Athlete table is in the alpha3 format"
        if birthday == '':
            birthdayStr: str = 'birthday is null'

        else:
            birthdayStr: str = f'birthday = "{birthday}"'
        if nation == '':
            nationStr: str = ''
        else:
            nationStr: str = f' AND nationAlpha3 = (SELECT alpha3 FROM nations WHERE IOC ="{nation}")'
        query: str = f'SELECT idAthlete FROM Athlete WHERE firstName = "{firstName}" AND lastName = "{lastName}"{nationStr} AND {birthdayStr};'

        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            result = connection.executeAndFetch(query)
            assert len(result) != 0, 'The query produced no result'
            assert len(result) == 1, 'The query did not give a unique result'
        return result[0][0]

    def __getColumnValues(self, columnName: 'str', tableWrapper: WebElement) -> List[WebElement]:
        elements: List[WebElement] = tableWrapper.find_elements(
            By.CSS_SELECTOR, f'td[data-th="{columnName}"]')
        return elements

    def __getAthleteId(self, table: WebElement) -> List[int]:
        tableWrapper: WebElement = table.find_element(By.TAG_NAME, 'tbody')

        time.sleep(8)
        firstNamesElements: List[WebElement] = self.__getColumnValues(
            columnName='givenName', tableWrapper=tableWrapper)
        firstNames: List[str] = list(map(lambda x: x.text, firstNamesElements))
        lastNamesElements: List[WebElement] = self.__getColumnValues(
            columnName='familyName', tableWrapper=tableWrapper)
        lastNames: List[str] = list(
            map(lambda x: x.text.upper(), lastNamesElements))
        nationElements: List[WebElement] = self.__getColumnValues(
            columnName='nat', tableWrapper=tableWrapper)
        nations: List[str] = list(map(lambda x: x.text, nationElements))
        linkBirthdays: list[WebElement] = tableWrapper.find_elements(
            By.TAG_NAME, 'a')
        assert len(linkBirthdays) == len(
            lastNames), "Maybe not all athletes have a link?"
        allAthleteIds: List[str] = [''] * len(linkBirthdays)
        for i, link in enumerate(linkBirthdays):
            self.drvr.get(link.get_attribute('href'))
            time.sleep(3)
            birthdayFindAll: List[str] = self.__findBirthday()
            if len(birthdayFindAll) == 0:
                birthday: str = ''
            else:
                birthday: str = birthdayFindAll[0]
            self.drvr.back()

            time.sleep(1)
            queryResult = self.__idQuery(
                firstName=firstNames[i], lastName=lastNames[i], nation=nations[i], birthday=birthday)
            allAthleteIds[i] = queryResult

        return allAthleteIds

    @staticmethod
    def __processShooting(row: pd.Series, index: int) -> int:
        if isinstance(row.Shootings, float):
            return ''
        else:
            shootingPresents = len(row.Shootings.split('+'))
            if index + 1 <= shootingPresents:
                return row.Shootings.split('+')[index]
            else:
                return ''

    @staticmethod
    def __processFinalRank(row: pd.Series) -> Tuple[str]:
        if row.finalRank.isdigit():
            return row.finalRank, 'Finished'
        else:
            return None, row.finalRank

    def getResultsTable(self) -> pd.DataFrame:
        table: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'table[id = "thistable"]')
        df: pd.DataFrame = pd.read_html(
            '<table>' + table.get_attribute('innerHTML') + '</table>')[0]
        lenTable: int = len(df)
        df['Family\xa0Name']: pd.Series = list(
            map(lambda x: x.upper(), df['Family\xa0Name']))
        allIds: List[int] = self.__getAthleteId(
            table=table)
        df['idAthlete']: pd.Series = allIds
        df['idRace']: pd.Series = [self.raceId] * lenTable
        nationElements: List[WebElement] = self.__getColumnValues(
            columnName='nat', tableWrapper=table)
        nations: List[str] = list(map(lambda x: x.text, nationElements))
        nationAlpha3: List[str] = [''] * lenTable
        for i in range(len(nationAlpha3)):
            query = f'SELECT alpha3 FROM nations WHERE IOC ="{nations[i]}"'
            with mySqlObject() as connection:
                connection.useDatabase('biathlon')

                result = connection.executeAndFetch(query)[0][0]
            nationAlpha3[i] = result
        df['nationAlpha3'] = nationAlpha3
        nShootings: int = ((len(df['Shootings'][0]) + 1) // 2)

        for i in range(nShootings):
            df[f'shooting{i+1}'] = df.apply(
                lambda row: self.__processShooting(row, i), axis=1)
            df[f'shooting{i+1}'] = df[f'shooting{i+1}'].apply(
                lambda x: x if x != '' else None)
        df.drop(columns=['Nation'], inplace=True)
        df.rename(columns={'Rank': 'finalRank', 'Bib': 'bib', 'Family\xa0Name': 'familyName',
                  'Given Name': 'givenName', 'Total': 'totalErrors', 'Shootings': 'shootings', 'Total Time': 'totalTime', 'Behind': 'behind'}, inplace=True)
        if 'Isolated Pursuit' in list(df.columns):
            df.rename(
                columns={'Isolated Pursuit': 'isolatedPursuit'}, inplace=True)
            df.isolatedPursuit = df.isolatedPursuit.apply(
                lambda x: x if isinstance(x, str) else None)
            df.isolatedPursuit = df.isolatedPursuit.apply(
                lambda x: '00:' + x if isinstance(x, str) and x.count(':') == 1 else x)
        df.behind = df.behind.apply(
            lambda x: x if isinstance(x, str) else None)
        df.totalTime = df.totalTime.apply(
            lambda x: x if isinstance(x, str) else None)
        df.behind = df.behind.apply(
            lambda x: x[1:] if isinstance(x, str) else x)
        df.behind = df.behind.apply(
            lambda x: '00:' + x if isinstance(x, str) and x.count(':') == 1 else x)
        df['totalTime'] = df['totalTime'].apply(
            lambda x: '00:' + x if isinstance(x, str) and x.count(':') == 1 else x)
        df.to_csv('tmp.csv', index=False)
        df['finishStatus'] = df.apply(
            lambda row: self.__processFinalRank(row)[1], axis=1)
        df.finalRank = df.apply(
            lambda row: self.__processFinalRank(row)[0], axis=1)

        return df
