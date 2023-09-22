from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from selenium.webdriver.common.by import By
from realBiathlon.mySql import mySqlObject
import time
from pprint import pprint
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.analysis import analysisHandle
from realBiathlon.usefuls import makeStringCamelCase
from typeguard import typechecked
import pandas as pd
import numpy as np


class splitTimesHandle:
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId
        self.athletesId: List[int] = getLoopTimes.getAthletesId(
            idRace=self.raceId)

    @typechecked
    def goToSplitTimes(self) -> None:
        spliTimesButton: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'label[id = "splitsB"]')
        spliTimesButton.click()

    @typechecked
    def getAllSplitTimesOptions(self) -> Tuple[List[WebElement], List[str]]:
        analysisHandle.clickDropDownElement(driver=self.drvr)
        time.sleep(.5)
        dropdownOptions: List[WebElement] = self.drvr.find_element(By.ID, "select2-loopsdropdown-results").find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        textOptions: List[str] = [option.text for option in dropdownOptions]

        finishIdx: int = textOptions.index('Finish')

        textOptions: List[str] = textOptions[1:finishIdx + 1]

        dropdownOptions: List[WebElement] = dropdownOptions[1:finishIdx + 1]

        '''
        textOptions: List[str] = list(map(lambda x: x.replace(
            'km', '').replace('→', 'entering').replace(' ', ''), textOptions))
        '''
        analysisHandle.clickDropDownElement(driver=self.drvr)

        return dropdownOptions, textOptions

    @typechecked
    def goToSplitTimesSection(self, textOption: str) -> None:
        analysisHandle.clickDropDownElement(driver=self.drvr)

        dropDownElement: WebElement = self.drvr.find_element(
            By.XPATH, f"//li[text()='{textOption}']")
        dropDownElement.click()

    @typechecked
    def getSplitTimesTables(self) -> pd.DataFrame:
        _, textOptions = self.getAllSplitTimesOptions()

        textOptions: List[str]

        allSplitTimesDf: List[pd.DataFrame] = []

        for text in textOptions:
            self.drvr.refresh()
            self.goToSplitTimesSection(textOption=text)
            tableHtml: str = self.drvr.find_element(
                By.ID, 'thistable').get_attribute('innerHTML')

            dfSpliTimes: pd.DataFrame = pd.read_html(
                '<table>' + tableHtml + '</table>')[0]

            assert len(dfSpliTimes) == len(
                self.athletesId), "Athlete id and dataframe do not correspond"

            dfSpliTimes['intermediate'] = text.replace(
                'km', '').replace('→', 'entering').replace(' ', '')

            dfSpliTimes['athleteId'] = self.athletesId

            dfSpliTimes['raceId'] = self.raceId

            dfSpliTimes = dfSpliTimes.drop(
                columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])

            dfSpliTimes.columns = list(
                map(lambda x: makeStringCamelCase(x), dfSpliTimes.columns))

            timeColumns: List[str] = ['sectorTime', 'netTime', 'dayTime']

            if np.all(list(map(lambda x: isinstance(x, float),
                           dfSpliTimes['behind']))):
                pass
            elif np.any(list(map(lambda x: isinstance(x, str),
                                 dfSpliTimes['behind']))):
                dfSpliTimes['behind'] = dfSpliTimes['behind'].apply(
                    lambda x: x[1:] if isinstance(x, str) and x.startswith('+') else x)
                timeColumns.append('behind')
            else:
                raise ValueError(
                    "Data is suppose to have either strings or floats")

            for column in timeColumns:
                dfSpliTimes[column] = getLoopTimes.handleTimeColumn(
                    columnName=column, df=dfSpliTimes)

            allSplitTimesDf.append(dfSpliTimes)
            time.sleep(1)

        finalSplitTimesDf: pd.DataFrame = pd.concat(
            allSplitTimesDf, ignore_index=True)

        return finalSplitTimesDf
