from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from selenium.webdriver.common.by import By
from realBiathlon.mySql import mySqlObject
import time
from pprint import pprint
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.usefuls import makeStringCamelCase
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
from typeguard import typechecked
from functools import reduce


class analysisHandle:
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId
        self.athletesId: List[int] = getLoopTimes.getAthletesId(
            idRace=self.raceId)

    @typechecked
    def goToAnalysis(self) -> None:
        time.sleep(1)
        analysisButton = WebDriverWait(self.drvr, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[id = "analysisB"]')))

        analysisButton.click()

    @staticmethod
    @typechecked
    def clickDropDownElement(driver: WebDriver) -> None:
        dropdownElement: WebElement = driver.find_element(
            By.ID, 'select2-loopsdropdown-container')
        dropdownElement.click()

    @typechecked
    def getAllAnalysisOptions(self) -> Tuple[List[WebElement], List[str]]:
        self.clickDropDownElement(driver=self.drvr)
        time.sleep(.5)
        dropdownOptions: List[WebElement] = self.drvr.find_element(By.ID, "select2-loopsdropdown-results").find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        textOptions = [option.text for option in dropdownOptions]

        self.clickDropDownElement(driver=self.drvr)

        return dropdownOptions, textOptions

    def goToAnalysisSection(self, textOption: str) -> None:
        self.clickDropDownElement(driver=self.drvr)

        dropDownElement: WebElement = self.drvr.find_element(
            By.XPATH, f"//li[text()='{textOption}']")
        dropDownElement.click()

    def getAnalysisTable(self, dropNation=True) -> pd.DataFrame:

        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')

        dfAnalysis: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]

        if dropNation:
            assert len(dfAnalysis) == len(
                self.athletesId), "Analysis dataframe and athlete ids did not match"

            dfAnalysis = dfAnalysis.drop(
                columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])
        else:
            dfAnalysis = dfAnalysis.drop(
                columns=['Rank', 'Bib', 'Country'])

        dfAnalysis.columns = list(
            map(lambda x: makeStringCamelCase(x), dfAnalysis.columns))

        return dfAnalysis

    @typechecked
    @staticmethod
    def joinAnalysisDf(leftDf: pd.DataFrame, rightDf: pd.DataFrame, on: str = 'athletesId') -> pd.DataFrame:
        newDf: pd.DataFrame = leftDf.merge(
            right=rightDf, on=on, how='inner')
        return newDf

    @typechecked
    def getAnalysisFinalTable(self) -> pd.DataFrame:
        _, textOptions = self.getAllAnalysisOptions()
        textOptions: List[str]
        allAnalysisDf: List[pd.DataFrame] = []
        for text in textOptions[1:-2]:
            self.goToAnalysisSection(text)
            time.sleep(1)
            analysisDf: pd.DataFrame = self.getAnalysisTable()

            analysisDf: pd.DataFrame = analysisDf.add_suffix(makeStringCamelCase(text)[0].upper() +
                                                             makeStringCamelCase(text)[1:])
            analysisDf['athletesId'] = self.athletesId
            allAnalysisDf.append(analysisDf)

        finalAnalysisDf: pd.DataFrame = reduce(lambda x, y: self.joinAnalysisDf(
            leftDf=x, rightDf=y), allAnalysisDf)

        finalAnalysisDf['raceId'] = self.raceId

        timeColumns: List[str] = ['totalTimeCourseTime',
                                  'rangeTimeAndPenaltyTimeShooting', 'totalTimeShootingTime', 'totalTimeRangeTime', 'totalTimeCumulativeTime']

        if np.all(list(map(lambda x: isinstance(x, float),
                           finalAnalysisDf['penaltyLoopAvgShooting']))):
            pass
        elif np.any(list(map(lambda x: isinstance(x, str),
                             finalAnalysisDf['penaltyLoopAvgShooting']))):
            timeColumns += ['penaltyLoopAvgShooting']
        else:
            raise ValueError(
                "Data is suppose to have either strings or floats")
        for column in timeColumns:
            finalAnalysisDf[column] = getLoopTimes.handleTimeColumn(
                columnName=column, df=finalAnalysisDf)

        return finalAnalysisDf
