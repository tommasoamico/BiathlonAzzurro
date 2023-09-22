from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Union, Tuple, Optional
import pandas as pd
from pprint import pprint
from realBiathlon.constants import specialCases
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from realBiathlon.mySql import mySqlObject
from typing import Type, Iterable, Any
from realBiathlon.loopTimes import getLoopTimes
from typeguard import typechecked
from realBiathlon.usefuls import makeStringCamelCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


class retrieveRaceResults:
    allInstances: List[Type] = []

    def __init__(self, driver: WebDriver, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId
        self.allInstances.append(self)

    def __findBirthday(self) -> List[str]:
        time.sleep(2)
        divBirthday: WebElement = self.drvr.find_element(
            By.ID, 'pagesubheaderright')
        birthday: List[str] = re.findall(
            r'\d{4}-\d{2}-\d{2}', divBirthday.text)
        return birthday

    @staticmethod
    def __idQuery(firstName: str, lastName: str, nation: str, birthday: str) -> int:
        logging.info(
            f'Issued query for {firstName} {lastName} of {nation}. Born in {birthday}')
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

        return result

    def __getColumnValues(self, columnName: 'str', tableWrapper: WebElement) -> List[WebElement]:
        elements: List[WebElement] = tableWrapper.find_elements(
            By.CSS_SELECTOR, f'td[data-th="{columnName}"]')
        return elements

    def __findFirstLastName(self) -> Tuple[str, str]:
        WebDriverWait(self.drvr, 20).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div[class = "athname"]')))
        athElement: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'div[class = "athname"]')

        athFullName: str = athElement.find_element(By.ID, 'content').text

        firstName: str = athFullName.split(' ')[0]

        lastName: str = athFullName[athFullName.index(' ') + 1:]

        return firstName, lastName.upper()

    def __getAthleteId(self, table: WebElement, booleanMask: Optional[Iterable[bool]] = None) -> List[int]:
        tableWrapper: WebElement = table.find_element(By.TAG_NAME, 'tbody')

        time.sleep(5)
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
        if booleanMask is not None:
            firstNames = np.array(firstNames)[booleanMask]
            lastNames = np.array(lastNames)[booleanMask]
            nations = np.array(nations)[booleanMask]
            linkBirthdays = np.array(linkBirthdays)[booleanMask]

        assert len(linkBirthdays) == len(
            lastNames), "Maybe not all athletes have a link?"
        allAthleteIds: List[str] = [''] * len(linkBirthdays)
        for i, link in enumerate(linkBirthdays):
            self.drvr.get(link.get_attribute('href'))
            time.sleep(3.5)
            birthdayFindAll: List[str] = self.__findBirthday()
            if len(birthdayFindAll) == 0:
                birthday: str = ''
            else:
                birthday: str = birthdayFindAll[0]

            queryResult = self.__idQuery(
                firstName=firstNames[i], lastName=lastNames[i], nation=nations[i], birthday=birthday)

            if len(queryResult) == 1:

                allAthleteIds[i] = queryResult[0][0]

            else:
                firstName, lastName = self.__findFirstLastName()

                queryResult = self.__idQuery(
                    firstName=firstName, lastName=lastName, nation=nations[i], birthday=birthday)

                assert len(
                    queryResult) == 1, f"There is a problem with {firstNames[i]} {lastNames[i]}"

                allAthleteIds[i] = queryResult[0][0]

            self.drvr.back()

            time.sleep(2)

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
        try:
            if row.finalRank.isdigit():
                return row.finalRank, 'Finished'
            else:
                return None, row.finalRank
        except AttributeError:
            return row.finalRank, 'Finished'

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

    @typechecked
    def getResultsTableTeam(self) -> pd.DataFrame:
        table: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'table[id = "thistable"]')
        df: pd.DataFrame = pd.read_html(
            '<table>' + table.get_attribute('innerHTML') + '</table>')[0]
        return df

    @staticmethod
    @typechecked
    def getAlpha3(ioc: str) -> str:
        queryStr = f'SELECT alpha3 FROM biathlon.nations WHERE IOC = "{ioc}"'

        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            resultQuery: List[Tuple[str]
                              ] = connection.executeAndFetch(queryStr)
        assert len(resultQuery) == 1, "The query did not provide a unique result"

        return resultQuery[0][0]

    @typechecked
    def getResultsNationsTeam(self, df: pd.DataFrame) -> pd.DataFrame:
        booleanMask: Iterable[bool] = ~ df['Country'].isna()
        countriesDf: pd.DataFrame = df[booleanMask]  # .reset_index(
        # drop=True)

        countriesDf: pd.DataFrame = countriesDf.drop(
            columns=['Family\xa0Name', 'Given Name', 'Country'])

        countriesDf['alpha3'] = countriesDf['Nation'].apply(
            lambda x: self.getAlpha3(x))

        countriesDf['Lapped'] = countriesDf['Total Time'].apply(
            lambda x: True if x == 'Lapped' else False)

        countriesDf['Total Time'] = countriesDf['Total Time'].apply(
            lambda x: x if np.logical_and(isinstance(x, str), x != 'Lapped') else None)

        for i, position in enumerate(['prone', 'standing']):
            countriesDf[f'{position}Shooting'] = countriesDf['Shootings'].apply(
                lambda x: x.split(' ')[i] if isinstance(x, str) else None)

        countriesDf: pd.DataFrame = countriesDf.drop(
            columns=['Nation', 'Shootings'])

        countriesDf['Behind'] = countriesDf['Behind'].apply(
            lambda x: x[1:] if isinstance(x, str) and x.startswith('+') else x)

        timeColumns: List[str] = ['Total Time', 'Behind']

        for column in timeColumns:
            countriesDf[column] = getLoopTimes.handleTimeColumn(
                columnName=column, df=countriesDf)

        countriesDf.columns = list(
            map(lambda x: makeStringCamelCase(x), countriesDf.columns))

        countriesDf = countriesDf.rename(
            columns={'total': 'totalErrors', 'rank': 'finalRank'})

        countriesDf['idRace'] = self.raceId

        return countriesDf

    @typechecked
    def __getNationResultId(self, ioc: str) -> int:

        queryStr: str = f'SELECT idraceResultsRelayNation FROM biathlon.raceResultsRelayNation WHERE idRace = {self.raceId} AND alpha3 = (SELECT alpha3 FROM biathlon.nations WHERE IOC = "{ioc}")'
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            idNationsTable: List[Tuple[int]
                                 ] = connection.executeAndFetch(queryStr)

            assert len(
                idNationsTable) == 1, "The query did not provide a unique result"

        return idNationsTable[0][0]

    @typechecked
    def getResultsAthletesTeam(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Remember to insert the nation entry id
        '''
        booleanMask: pd.Series = df['Country'].isna()
        athletesDf: pd.DataFrame = df[booleanMask]
        athletesDf['bibNation'] = athletesDf['Bib'].apply(
            lambda x: x.split('-')[0] if isinstance(x, str) else x)
        athletesDf['legBib'] = athletesDf['Bib'].apply(
            lambda x: x.split('-')[1] if isinstance(x, str) else x)
        athletesDf: pd.DataFrame = athletesDf.drop(
            columns=['Behind', 'Country', 'Bib'])

        idNationsTable: pd.Series = athletesDf.apply(
            lambda x: self.__getNationResultId(ioc=x.Nation), axis=1)
        athletesDf['idraceResultsRelayNation'] = idNationsTable
        athletesId: List[int] = self.__getAthleteId(
            self.drvr.find_element(By.CSS_SELECTOR, 'table[id = "thistable"]'), booleanMask=booleanMask)
        assert len(athletesId) == len(
            athletesDf), 'Number of Ids do not match length of dataframe'
        athletesDf['athletesId'] = athletesId
        athletesDf['lapped'] = athletesDf['Total Time'].apply(
            lambda x: True if x == 'Lapped' else False)

        athletesDf['Total Time'] = athletesDf['Total Time'].apply(
            lambda x: x if np.logical_and(isinstance(x, str), x != 'Lapped') else None)

        athletesDf['Total Time'] = getLoopTimes.handleTimeColumn(
            columnName='Total Time', df=athletesDf)

        for i, position in enumerate(['prone', 'standing']):
            athletesDf[f'{position}Shooting'] = athletesDf['Shootings'].apply(
                lambda x: x.split(' ')[i] if isinstance(x, str) else None)

        athletesDf['alpha3'] = athletesDf['Nation'].apply(
            lambda x: self.getAlpha3(x))

        athletesDf: pd.DataFrame = athletesDf.drop(
            columns=['Rank', 'Family\xa0Name', 'Given Name', 'Nation', 'Shootings'])

        athletesDf: pd.DataFrame = athletesDf.rename(
            columns={'Total': 'totalErrors', 'Total Time': 'totalTime'})

        return athletesDf
