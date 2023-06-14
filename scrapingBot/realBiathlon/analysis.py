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
import numpy as np


class analysisHandle:
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId

    def goToAnalysis(self) -> Tuple[List[WebElement], List[str]]:
        analysisButton: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'label[id = "analysisB"]')
        analysisButton.click()

    def __clickDropDownElement(self) -> WebElement:
        dropdownElement: WebElement = self.drvr.find_element(
            By.ID, 'select2-loopsdropdown-container')
        dropdownElement.click()

    def getAllAnalysisOptions(self) -> Tuple[List[WebElement], List[str]]:
        self.__clickDropDownElement()
        time.sleep(.5)
        dropdownOptions: List[WebElement] = self.drvr.find_element(By.ID, "select2-loopsdropdown-results").find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        textOptions = [option.text for option in dropdownOptions]

        self.__clickDropDownElement()

        return dropdownOptions, textOptions

    def goToAnalysisSection(self, textOption: str) -> None:
        self.__clickDropDownElement()

        dropDownElement: WebElement = self.drvr.find_element(
            By.XPATH, f"//li[text()='{textOption}']")
        dropDownElement.click()

    def getAnalysisTable(self) -> pd.DataFrame:
        athletesId: List[int] = getLoopTimes.getAthletesId(idRace=self.raceId)

        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')

        dfAnalysis: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]

        assert len(dfAnalysis) == len(
            athletesId), "Analysis dataframe and athlete ids did not match"

        dfAnalysis = dfAnalysis.drop(
            columns=['Bib', 'Family\xa0Name', 'Given Name', 'Nation'])

        dfAnalysis.columns = list(
            map(lambda x: makeStringCamelCase(x), dfAnalysis.columns))

        return dfAnalysis

    def joinAnalysisDf(self) -> None:
        pass
