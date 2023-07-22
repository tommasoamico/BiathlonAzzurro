from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple, Optional
from selenium.webdriver.common.by import By
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.raceResults import retrieveRaceResults
from typeguard import typechecked
from pprint import pprint
from realBiathlon.mySql import mySqlObject
from realBiathlon.usefuls import makeStringCamelCase
import pandas as pd


class getLoopTimesRelay(getLoopTimes):
    def __init__(self, driver: WebElement, raceId: int) -> None:
        super().__init__(driver, raceId)

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
    @staticmethod
    def getAthletesRelayId(idRace: int, athleteNumber: str) -> List[int]:
        if athleteNumber == 'Σ':
            idQuery: str = f'SELECT athletesId FROM raceResultsRelayAthletes ra WHERE (SELECT rn.idRace FROM raceResultsRelayNation rn WHERE ra.idRaceResultsRelayNation = rn.idraceResultsRelayNation) = {idRace}'

        else:
            idQuery: str = f'SELECT athletesId FROM raceResultsRelayAthletes ra WHERE (SELECT rn.idRace FROM raceResultsRelayNation rn WHERE ra.idRaceResultsRelayNation = rn.idraceResultsRelayNation) = {idRace} AND legBib = {int(athleteNumber)}'
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            idQueried: List[Tuple[int]
                            ] = connection.executeAndFetch(idQuery)

        idAthletes: List[int] = list(map(lambda x: x[0], idQueried))

        return idAthletes

    @typechecked
    def getLoopTableRelay(self, athleteNumber: str, loopNumber: str) -> pd.DataFrame:
        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')
        dfAthlete: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]

        if athleteNumber == 'Σ':

            dfAthlete = dfAthlete.drop(
                columns=['Rank', 'Bib', 'Country'])
            timeColumns = ['Cumulative Time',
                           'Loop Time', 'Course Time']

            for column in timeColumns:
                dfAthlete[column] = self.handleTimeColumn(
                    columnName=column, df=dfAthlete)

            dfAthlete['alpha3'] = dfAthlete['Nation'].apply(
                lambda x: retrieveRaceResults.getAlpha3(x))
            dfAthlete: pd.DataFrame = dfAthlete.drop(columns='Nation')
        else:
            dfAthlete: pd.DataFrame = dfAthlete.drop(
                columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])
            for column in dfAthlete.columns:
                dfAthlete[column] = self.handleTimeColumn(
                    columnName=column, df=dfAthlete)
            athletesId: List[int] = self.getAthletesRelayId(
                idRace=self.raceId, athleteNumber=athleteNumber)
            assert len(athletesId) == len(
                dfAthlete), "Number of athletes and ids differ"
            dfAthlete['athletesId'] = athletesId

        dfAthlete.columns = list(
            map(lambda x: makeStringCamelCase(x), dfAthlete.columns))
        dfAthlete['idRace'] = self.raceId
        dfAthlete['athleteNumber'] = athleteNumber
        dfAthlete['loopNumber'] = loopNumber

        return dfAthlete
