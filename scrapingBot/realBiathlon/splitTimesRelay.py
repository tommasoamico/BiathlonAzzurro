from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from typing import List, Tuple
from selenium.webdriver.common.by import By
from realBiathlon.mySql import mySqlObject
import time
from pprint import pprint
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.splitTimes import splitTimesHandle
from realBiathlon.usefuls import makeStringCamelCase
from typeguard import typechecked
import pandas as pd
import numpy as np


class splitTimesHandleRelay(splitTimesHandle):
    def __init__(self, driver: WebElement, raceId: int) -> None:
        super(splitTimesHandleRelay, self).__init__(driver, raceId)

    @typechecked
    def getSplitTimesRelayTable(self) -> pd.DataFrame:
        _, textOptions = super(splitTimesHandleRelay,
                               self).getAllSplitTimesOptions()

        textOptions: List[str]

        allSplitTimesDf: List[pd.DataFrame] = []

        for text in textOptions:
            time.sleep(1)
            super(splitTimesHandleRelay, self).goToSplitTimesSection(
                textOption=text)

            tableHtml: str = self.drvr.find_element(
                By.ID, 'thistable').get_attribute('innerHTML')

            dfSpliTimes: pd.DataFrame = pd.read_html(
                '<table>' + tableHtml + '</table>')[0]

            dfSpliTimes['intermediate'] = text.replace(
                'km', '').replace('→', 'entering').replace(' ', '')

            dfSpliTimes['raceId'] = self.raceId

            dfSpliTimes = dfSpliTimes.drop(
                columns=['Rank', 'Bib', 'Country'])

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

        finalSplitTimesDf: pd.DataFrame = pd.concat(
            allSplitTimesDf, ignore_index=True)

        finalSplitTimesDf: pd.DataFrame = finalSplitTimesDf.rename(columns={
                                                                   'nation': 'ioc'})

        return finalSplitTimesDf
