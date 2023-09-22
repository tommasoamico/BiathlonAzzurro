from typing import List, Type, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from realBiathlon.constants import mainUrl
import os
import time
import re
import numpy as np
from datetime import datetime
from realBiathlon.mySql import mySqlObject
from itertools import repeat
import pandas as pd
from realBiathlon.raceResults import retrieveRaceResults
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.loopTimesRelay import getLoopTimesRelay
from realBiathlon.shooting import getShooting
from realBiathlon.shootingRelay import getShootingRelay
from realBiathlon.analysis import analysisHandle
from realBiathlon.analysisRelay import analysisHandleRelay
from realBiathlon.splitTimesRelay import splitTimesHandleRelay
from realBiathlon.splitTimes import splitTimesHandle
from realBiathlon.metadata import metadataHandle
# from realBiathlon.metadataRelay import metadataHandleRelay
from typeguard import typechecked


class races(webdriver.Chrome):
    all: List[Type] = []

    def __init__(self, year: int, level: str, driverPath: str = r'/Users/tommaso/Workspace/seleniumDrivers/chromedriver-mac-x64',
                 teardown: bool = False) -> None:
        assert isinstance(year, int), 'Year must be an integer'
        assert level in [
            'World', 'IBU', 'Y/J'], 'level argument must be either World, IBU or Y/J'
        self.year: int = year
        pattern = re.compile('^[0-9]{4}')
        minimum: int = 1958
        # If post may we add a year
        maximum: int = round((datetime.now().month + 2) / 12, 0) + self.year
        assert pattern.search(str(
            year)), 'The year must be an integer number of length 4 pointing to the year in which the season ends, minimum is 1958'
        assert np.logical_and(
            year > minimum, year < maximum), f"Year must be between {minimum} and {maximum}"
        self.driverPath: str = driverPath
        self.teardown: bool = teardown

        self.levelDict = {'World': 1, 'IBU': 2, 'Youth': 3}
        self.level = level
        self.yearDataBase = f'{self.year - 1}-{str(self.year)[-2:]}'
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        os.environ['PATH'] += self.driverPath

        super(races, self).__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print('Exiting...')
        if self.teardown:
            self.quit()

    def landInRealBiathlon(self) -> None:
        self.get(mainUrl)

    def goToRaces(self) -> None:
        raceButton = self.find_element(
            By.CSS_SELECTOR,
            'a[href = "races.html"]')

        raceButton.click()

    def __getAllYears(self) -> List[str]:
        time.sleep(1)
        yearDropdown = self.find_element(
            By.ID,
            'select2-years-container')
        yearDropdown.click()
        time.sleep(.5)
        ulElement = self.find_element(By.ID,
                                      'select2-years-results')
        liElements = ulElement.find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        return [element.get_property("id") for element in liElements]

    def selectYear(self) -> None:

        rightIdList: List[str] = list(
            filter(lambda x: str(self.year) in x, self.__getAllYears()))
        assert len(
            rightIdList) == 1, 'The filtering didn\'t bring to a unique result'

        yearDropdown: WebElement = self.find_element(By.ID,
                                                     rightIdList[0])

        yearDropdown.click()

    def selectLevel(self) -> None:

        time.sleep(.5)
        levelButton: WebElement = self.find_element(By.ID,
                                                    f'{self.levelDict[self.level]}button')
        levelButton.click()

    def selectGender(self, gender: str) -> None:
        time.sleep(.5)
        assert gender == "W" or gender == "M", 'Gender must be one of M or W'

        genderButton = self.find_element(
            By.ID,
            gender + 'button')

        genderButton.click()

    def __idStageQuery(self, locations: List[str], eventNumbers: List[str]) -> List[int]:
        nObjects: int = len(locations)
        # print([(level, location, season, eventNumber)
        #      for level, location, season, eventNumber in zip(repeat(self.level, nObjects), locations, repeat(self.yearDataBase, nObjects), eventNumbers)])
        parameters = [(level, location, season, eventNumber)
                      for level, location, season, eventNumber in zip(repeat(self.level, nObjects), locations, repeat(self.yearDataBase, nObjects), eventNumbers)]

        with mySqlObject() as connection:
            connection.useDatabase('biathlon')

            query = "SELECT idStage FROM stage WHERE level = '%s' AND location = '%s' AND season = '%s' AND eventNumber = '%s'"
            results = []
            for parameter in parameters:
                connection.dbc.execute(query % parameter)
                result = connection.dbc.fetchall()[0]
                assert len(
                    result) == 1, "The query did not get an unique result"
                results.append(result[0])

            return results

    def __getHeaders(self) -> List[WebElement]:
        stageHeadersElement: List[WebElement] = self.find_elements(
            By.CSS_SELECTOR, 'h4[id = "content"]')

        return stageHeadersElement

    def __getTables(self) -> List[WebElement]:
        time.sleep(1)
        tablesElements: List[WebElement] = self.find_elements(
            By.CSS_SELECTOR, 'table[id = "thistable"]')
        return tablesElements

    def __idStatusRaceQuery(self, stageIterables: list, dates: List[str], descriptions: List[Tuple[str]]):
        query = "SELECT idRace, status FROM race WHERE idStage = '%s' AND date = '%s' AND description = '%s'"

        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            results = []
            for stage, date, description in zip(stageIterables, dates, descriptions):
                result = connection.executeAndFetch(
                    query % (stage, date, description))[0]
                assert len(
                    result) == 2, "The query did not get an unique result"
                results.append(result)
            return results

    def findAllStagesAndRaces(self) -> dict:
        time.sleep(3)
        stageHeadersElement = self.__getHeaders()
        allHeaders = [header.text for header in stageHeadersElement]
        allLocations = list(map(lambda x: x.split('(')[0].strip(), allHeaders))
        allEventNumbers = list(map(lambda x: x.split(' ')[-1], allHeaders))
        allIds: List[int] = self.__idStageQuery(
            locations=allLocations, eventNumbers=allEventNumbers)
        allTables = self.__getTables()
        assert len(allTables) == len(
            allHeaders), 'Stages and Tables did not match'
        allTablesWithTag = list(
            map(lambda x: '<table>' + x.get_attribute('innerHTML') + '</table>', allTables))
        allDf = list(map(lambda x: pd.read_html(x)[0], allTablesWithTag))
        lenStages = list(map(lambda x: len(x), allDf))
        stageRaceDict: dict = {}
        allDescriptions = list(map(lambda x: list(x['Description']), allDf))
        allDates = list(map(lambda x: list(x['Date']), allDf))
        stagesIdIterables = list(
            map(lambda x, y: repeat(x, y), allIds, lenStages))

        for i, (stageIterables, dates, descriptions) in enumerate(zip(stagesIdIterables, allDates, allDescriptions)):
            stageRaceDict[allIds[i]] = self.__idStatusRaceQuery(
                stageIterables=stageIterables, dates=dates, descriptions=descriptions)
        return stageRaceDict

    def clickRace(self, stagePosition: int, racePosition: int) -> None:
        allTables: List[WebElement] = self.__getTables()
        myTable: WebElement = allTables[stagePosition]
        cilckablRaces: List[WebElement] = myTable.find_elements(
            By.TAG_NAME, "tr")
        race: WebElement = cilckablRaces[racePosition + 1].find_element(
            By.CSS_SELECTOR, 'td[data-th="status"]')

        race.click()

        # cilckablRaces[racePosition + 1].click()  # header has a tr

        # print(len(cilckableElements))

    def getAllClickableSections(self) -> List[str]:
        divElement: WebElement = self.find_element(
            By.CSS_SELECTOR, 'div[id = "cat"]')
        allOptions: List[WebElement] = divElement.find_elements(
            By.TAG_NAME, 'label')
        time.sleep(1)
        allOptionsText: List[str] = [option.text for option in allOptions]
        assert np.all([option != '' for option in allOptionsText]
                      ), "Options html did not load"

        return allOptionsText

    def getRaceResult(self, raceId: int) -> Type[retrieveRaceResults]:
        return retrieveRaceResults(self, raceId=raceId)

    def getRaceStatus(self, raceId: int) -> str:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            status = connection.executeAndFetch(
                f'SELECT status FROM biathlon.race WHERE idRace = {raceId};')
            assert len(status) == 1, "The query did not provide a unique result"
            return status[0][0]

    def getRaceInsertStatus(self, raceId: int) -> str:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            insertStatus = connection.executeAndFetch(
                f'SELECT insertStatus FROM biathlon.race WHERE idRace = {raceId};')
            assert len(
                insertStatus) == 1, "The query did not provide a unique result"
            return insertStatus[0][0]

    def adjustStatus(self, raceId: int, statusRealBiathlon: str) -> None:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            connection.executeAndCommit(
                f'UPDATE race SET status = "{statusRealBiathlon}" WHERE idRace = {raceId}')

    def insertIntoTableDf(self, tableName: str, df: pd.DataFrame) -> None:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            connection.insertFromDf(tableName=tableName, df=df)

    @staticmethod
    def setInstertState(raceId: int) -> None:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            connection.executeAndCommit(
                f'UPDATE race SET insertStatus = "inserted" WHERE (idRace = {raceId});')

    @staticmethod
    @typechecked
    def getGeneraCategory(raceId: int) -> str:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            generalCategory: List[Tuple[str]] = connection.executeAndFetch(
                f"SELECT generalCategory FROM biathlon.race WHERE idRace = {raceId}")
        assert len(
            generalCategory) == 1, "General Category query did not provide a unique result"
        return generalCategory[0][0]

    def getLoopTimes(self, raceId: int) -> Type[getLoopTimes]:
        return getLoopTimes(driver=self, raceId=raceId)

    def getLoopTimesRelay(self, raceId: int) -> Type[getLoopTimesRelay]:
        return getLoopTimesRelay(driver=self, raceId=raceId)

    def getShootingResults(self, raceId: int) -> Type[getShooting]:
        return getShooting(driver=self, idRace=raceId)

    def getShootingResultsRelay(self, raceId: int) -> Type[getShootingRelay]:
        return getShootingRelay(driver=self, idRace=raceId)

    def getAnalysis(self, raceId: int) -> Type[analysisHandle]:
        return analysisHandle(driver=self, raceId=raceId)

    def getAnalysisRelay(self, raceId: int) -> Type[analysisHandleRelay]:
        return analysisHandleRelay(driver=self, raceId=raceId)

    def getSplitTimes(self, raceId) -> Type[splitTimesHandle]:
        return splitTimesHandle(driver=self, raceId=raceId)

    def getSplitTimesRelay(self, raceId) -> Type[splitTimesHandleRelay]:
        return splitTimesHandleRelay(driver=self, raceId=raceId)

    def getMetadata(self, raceId) -> Type[metadataHandle]:
        return metadataHandle(driver=self, raceId=raceId)

    # def getMetadataRelay(self, raceId) -> Type[metadataHandleRelay]:
    #    return metadataHandleRelay(driver=self, raceId=raceId)

# Insert the cancelled status case
