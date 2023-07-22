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
from realBiathlon.analysis import analysisHandle
import numpy as np
from typeguard import typechecked
from functools import reduce
from realBiathlon.usefuls import makeStringCamelCase


class analysisHandleRelay(analysisHandle):
    def __init__(self, driver: WebElement, raceId: int) -> None:
        self.drvr: WebDriver = driver
        self.raceId: int = raceId

    @typechecked
    def getAnalysisFinalTableRelay(self) -> pd.DataFrame:
        _, textOptions = super().getAllAnalysisOptions()
        textOptions: List[str]
        allAnalysisDf: List[pd.DataFrame] = []
        for text in textOptions[1:-2]:
            self.goToAnalysisSection(text)
            time.sleep(1)
            analysisDf: pd.DataFrame = super().getAnalysisTable(dropNation=False)

            analysisDf: pd.DataFrame = analysisDf.add_suffix(makeStringCamelCase(text)[0].upper() +
                                                             makeStringCamelCase(text)[1:])

            analysisDf: pd.DataFrame = analysisDf.rename(columns={'nation' + makeStringCamelCase(text)[0].upper() +
                                                                  makeStringCamelCase(text)[1:]: 'ioc'})
            # print('nation' + makeStringCamelCase(text)[0].upper() +
            #     makeStringCamelCase(text)[1:])
            allAnalysisDf.append(analysisDf)
            # pprint(analysisDf.columns)
        finalAnalysisDf: pd.DataFrame = reduce(lambda x, y: super(analysisHandleRelay, self).joinAnalysisDf(
            leftDf=x, rightDf=y, on='ioc'), allAnalysisDf)

        finalAnalysisDf['raceId'] = self.raceId

        timeColumns: List[str] = list(
            filter(lambda x: 'Time' in x, finalAnalysisDf.columns))

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

        rankColumns: List[str] = [
            'totalcourseTimeRankCourseTime', 'totalrangeTimeRankRangeTime', 'totalrangeTimestandingRankRangeTimeStanding', 'totalshootingTimeRankShootingTime', 'totalrangeTimeproneRankRangeTimeProne', 'totalshootingTimestandingRankShootingTimeStanding',
            'totalshootingTimeproneRankShootingTimeProne']

        for columnRank in rankColumns:
            print(finalAnalysisDf[columnRank][0],
                  type(finalAnalysisDf[columnRank][0]))
            finalAnalysisDf[columnRank] = finalAnalysisDf[columnRank].apply(
                lambda x: x if x.isdigit() else None)

        finalAnalysisDf['lapped'] = finalAnalysisDf['totalcourseTimeRankCourseTime'].apply(
            lambda x: True if x == 'LAP' else False)

        return finalAnalysisDf
        # return finalAnalysisDf
