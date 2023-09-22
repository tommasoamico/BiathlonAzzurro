from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Generator, List, Tuple, Any
from selenium.webdriver.common.by import By
from realBiathlon.mySql import mySqlObject
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pprint import pprint
import pandas as pd
from realBiathlon.shooting import getShooting
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.loopTimesRelay import getLoopTimesRelay
from typeguard import typechecked
from realBiathlon.constants import nTargets
import re


class getShootingRelay(getShooting):
    def __init__(self, driver: WebDriver, idRace: int) -> None:
        super().__init__(driver, idRace)
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            self.raceDescription: str = connection.executeAndFetch(
                f"SELECT description FROM race WHERE idRace='{idRace}';")[0][0]

    @typechecked
    def getAllAthleteFields(self) -> Tuple[List[WebElement], List[str]]:
        athletesDiv = self.drvr.find_element(By.ID, 'relayathletegroup')
        athleteElements = athletesDiv.find_elements(By.TAG_NAME, 'label')
        athleteText = [
            athleteElement.text for athleteElement in athleteElements]
        noAthleteIndexes = [i for i, x in enumerate(athleteText) if x == '']
        filteredAthleteText = [loop for i, loop in enumerate(
            athleteText) if i not in noAthleteIndexes]
        filteredAthleteElements = [loop for i, loop in enumerate(
            athleteElements) if i not in noAthleteIndexes]
        return filteredAthleteElements, filteredAthleteText

    @typechecked
    def getShootingTableRelay(self) -> Generator[pd.DataFrame, None, None]:

        # athleteElements, athleteTexts = self.getAllAthleteFields()

        # athleteElements: List[WebElement]
        # athleteTexts: List[str]

        # for element, text in zip(athleteElements, athleteTexts):
        time.sleep(1)
        # getLoopTimes.clickElement(element)
        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')

        dfShootingRelay: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]

        # if text == 'Σ':
        athletesId: List[int] = getLoopTimesRelay.getAthletesRelayId(
            idRace=self.idRace, athleteNumber='Σ', raceDescription=self.raceDescription)
        # print()
        assert len(athletesId) == len(
            dfShootingRelay), "Number of athletes id and length of dataframes differ"
        # else:
        #   athletesId: List[int] = getLoopTimesRelay.getAthletesRelayId(
        #      idRace=self.idRace, athleteNumber=text)
        # assert len(athletesId) == len(dfShootingRelay)

        dfShootingRelay: pd.DataFrame = dfShootingRelay.drop(
            columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])
        dfShootingRelay.columns: List[str] = self.manouverRepeatedColumns(
            dfShootingRelay)

        shootingColumns = list(
            filter(lambda x: 'Shooting' in x, dfShootingRelay.columns))
        nShootings: int = len(shootingColumns)
        for column in shootingColumns:
            dfShootingRelay[f'shootingOrder{column[-1]}']: pd.Series = dfShootingRelay.apply(lambda x: x[column].split(
                ' ')[-1] if isinstance(x[column], str) else None, axis=1)
            dfShootingRelay[f'shooting{column[-1]}StartedFrom']: pd.Series = dfShootingRelay.apply(
                lambda x: self.decideStarting(x[f'shootingOrder{column[-1]}']) if isinstance(x[f'shootingOrder{column[-1]}'], str) else None, axis=1)
            for target in range(nTargets):
                dfShootingRelay[f'time{column[-1]}Target{target + 1}']: pd.Series = dfShootingRelay.apply(lambda x: self.timeShootings(
                    x[column], target) if isinstance(x[column], str) else None, axis=1)

            dfShootingRelay: pd.DataFrame = dfShootingRelay.drop(columns=[
                column])
        for i in range(nShootings):
            filteredDf: pd.DataFrame = dfShootingRelay[list(filter(lambda x: re.search(
                r"\d{1}", x).group() == f'{i + 1}', dfShootingRelay.columns))]
            filteredDf.columns = [column.replace(
                f'{i + 1}', '', 1) for column in filteredDf.columns]

            filteredDf['rangeNumber']: pd.Series = i + 1

            filteredDf['idAthlete'] = athletesId

            filteredDf['idRace'] = self.idRace

            # filteredDf['athleteNumber'] = text

            filteredDf = filteredDf.rename(
                columns={'Lane': 'lane', 'Time': 'shootingTime'})
            [i + 1 for i in range(5)]

            timeColumns: List[str] = [
                'shootingTime'] + list(filter(lambda x: 'timeTarget' in x, filteredDf.columns))

            for column in timeColumns:
                filteredDf[column] = getLoopTimes.handleTimeColumn(
                    columnName=column, df=filteredDf)

            yield filteredDf
            # yield filteredDf
