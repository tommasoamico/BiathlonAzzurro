from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from selenium.webdriver.common.by import By
from realBiathlon.mySql import mySqlObject
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pprint import pprint
import pandas as pd


class getLoopTimes:
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId

    def goToLoops(self) -> None:
        loopsButton: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'label[id = "detailsB"]')
        loopsButton.click()

    def getAllLoops(self) -> Tuple[List[WebElement], List[str]]:
        loopDiv = self.drvr.find_element(By.ID, 'loopsgroup')
        loopElements = loopDiv.find_elements(By.TAG_NAME, 'label')
        loopsText = [loopElement.text for loopElement in loopElements]
        noLoopIndexes = [i for i, x in enumerate(loopsText) if x == '']
        filteredLoopsText = [loop for i, loop in enumerate(
            loopsText) if i not in noLoopIndexes]
        filteredLoopElements = [loop for i, loop in enumerate(
            loopElements) if i not in noLoopIndexes]
        return filteredLoopElements, filteredLoopsText

    @staticmethod
    def clickElement(loopElement: WebElement) -> None:
        time.sleep(.6)
        loopElement.click()

    def switchToAbsoluteTimes(self) -> None:
        absoluteTimesSwitch = self.drvr.find_element(
            By.CSS_SELECTOR, 'label[for="behindSwitch"]')
        absoluteTimesSwitch.click()

    @staticmethod
    def getAthletesId(idRace: int) -> List[int]:
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            idAndRank: List[Tuple[int, str]] = connection.executeAndFetch(
                f"SELECT idAthlete, finalRank FROM raceResults WHERE idRace = {idRace} ORDER BY finalRank;")

        print(
            f"SELECT idAthlete, finalRank FROM raceResults WHERE idRace = {idRace} ORDER BY finalRank;")
        filteredidAndRank: List[Tuple[int, str]] = list(filter(
            lambda x: isinstance(x[1], int), idAndRank))
        filteredidAndRank
        idAthletes: List[Tuple[int, str]] = list(
            map(lambda x: x[0], filteredidAndRank))
        print(idAthletes)
        return idAthletes

    @staticmethod
    def convertStringToTime(timeStr: str):

        if isinstance(timeStr, str) and timeStr.count(':') == 1:

            timeStr = '00:' + timeStr

            if float(timeStr.split(':')[-1]) >= 60:
                seconds = float(timeStr.split(':')[-1]) - 1
                timeStr = ':'.join(timeStr.split(
                    ':')[:-1]) + ':' + str(seconds)

                return timeStr
            else:
                return timeStr
        else:

            try:
                if str(timeStr).count(':') == 0 and float(timeStr) >= 60:
                    timeStr = str(59.9)
            except (TypeError, ValueError):
                pass

            else:
                return timeStr

    @staticmethod
    def handleTimeColumn(columnName: str, df: pd.DataFrame) -> pd.Series:

        newColumn: pd.Series = df[columnName].apply(lambda x:
                                                    getLoopTimes.convertStringToTime(x))

        return newColumn

    def getLoopTable(self, loopNumber: str) -> pd.DataFrame:
        idAthletes: List[int] = self.getAthletesId(idRace=self.raceId)

        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')
        dfLoop: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]

        assert len(dfLoop) == len(
            idAthletes), "Loop dataframe and athlete ids did not match"
        dfLoop = dfLoop.rename(columns={'Cumulative Time': 'cumulativeTime', 'Ski Time': 'skiTime', 'Course Time': 'courseTime', 'Loop Time': 'loopTime',
                               'Range Time': 'rangeTime', 'Shooting Time': 'shootingTime', 'Penalty Time': 'penaltyTime'})
        dfLoop = dfLoop.drop(
            columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])
        for column in dfLoop.columns:
            dfLoop[column] = self.handleTimeColumn(
                columnName=column, df=dfLoop)
        dfLoop['idRace'] = self.raceId

        dfLoop['idAthlete'] = idAthletes
        dfLoop['loopNumber'] = loopNumber

        return dfLoop
