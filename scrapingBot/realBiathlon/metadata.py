from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from selenium.webdriver.common.by import By
import time
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.usefuls import makeStringCamelCase
from typeguard import typechecked
import pandas as pd
from pprint import pprint
import numpy as np


class metadataHandle:
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId
        self.athletesId: List[int] = getLoopTimes.getAthletesId(
            idRace=self.raceId)

    @typechecked
    def goToMetadata(self) -> None:
        analysisButton: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'label[id = "metaB"]')
        analysisButton.click()

    @staticmethod
    @typechecked
    def __customIsdigit(string) -> np.bool_:
        return np.logical_or(string.isdigit(), string[:-1].isdigit())

    @typechecked
    def getMetadataTable(self) -> pd.DataFrame:
        weatherAndCourseTable: List[WebElement] = self.drvr.find_elements(
            By.ID, 'thistable')

        weatherTableHtml: str = weatherAndCourseTable[0].get_attribute(
            'innerHTML')

        dfWeather: pd.DataFrame = pd.read_html(
            '<table>' + weatherTableHtml + '</table>')[0]

        dfWeather: pd.DataFrame = dfWeather.set_index('Unnamed: 0', drop=True)

        dfWeather.loc['windDirection'] = dfWeather.loc['Wind'].apply(
            lambda x: x.split('/')[0].strip())

        dfWeather.loc['windSpeed'] = dfWeather.loc['Wind'].apply(
            lambda x: (x.split('/')[1] + x.split('/')[2]).strip())

        dfWeather: pd.DataFrame = dfWeather.drop(index='Wind')

        dfWeather: pd.DataFrame = dfWeather.T

        dfWeather['time'] = dfWeather.index

        dfWeather = dfWeather.reset_index(drop=True)

        courseTableHtml: str = weatherAndCourseTable[1].get_attribute(
            'innerHTML')

        dfCourse: pd.DataFrame = pd.read_html(
            '<table>' + courseTableHtml + '</table>')[0]

        dfCourse: pd.DataFrame = dfCourse.set_index('Unnamed: 0', drop=True)

        dfCourse: pd.DataFrame = dfCourse.T

        dfCourse: pd.DataFrame = dfCourse.reset_index(drop=True)

        courseInformation: str = self.drvr.find_element(
            By.CSS_SELECTOR, 'h5[class="courseloop"]').text

        # splittedCourseInformation: List[str] = courseInformation.split(' ')

        # filteredCourse: List[str] = list(
        #    filter(lambda x: self.__customIsdigit(x), splittedCourseInformation))

        # assert len(
        #    filteredCourse) == 2, "Something went wrong in retrieving number of loops and length of the loop"

        dfWeather.columns = list(
            map(lambda x: makeStringCamelCase(x), dfWeather.columns))

        dfCourse.columns = list(
            map(lambda x: makeStringCamelCase(x) + 'InMetres', dfCourse.columns))

        # dfCourse['nLoops'] = filteredCourse[0]

        dfCourse['courseData'] = courseInformation

        dfMetadata: pd.DataFrame = pd.concat([dfWeather, dfCourse])

        dfMetadata['raceId'] = self.raceId

        return dfMetadata

        # pprint(dfMetadata)
