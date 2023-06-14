from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from realBiathlon.loopTimes import getLoopTimes
from realBiathlon.constants import nTargets
from typing import List
import pandas as pd
from pprint import pprint
import numpy as np
import re
from typing import Generator


class getShooting:
    def __init__(self, driver: WebDriver, idRace: int) -> None:
        self.drvr = driver
        self.idRace = idRace

    def goToShooting(self) -> None:
        shootingButton: WebElement = self.drvr.find_element(By.ID, 'shootingB')
        shootingButton.click()

    @staticmethod
    def __manouverRepeatedColumns(df: pd.DataFrame) -> List[str]:
        repeatedColumns: List[str] = list(map(lambda x: x.split(
            '.')[0], filter(lambda x: '.' in x, df.columns)))

        newColumns: list = []
        repeatedCount: dict = {
            repeatedColumn: 1 for repeatedColumn in repeatedColumns}
        for column in df.columns:
            splittedColumn: List[str] = column.split('.')[0]
            if splittedColumn in repeatedColumns:

                newColumns.append(
                    splittedColumn + str(repeatedCount[splittedColumn]))
                repeatedCount[splittedColumn] += 1
            else:
                newColumns.append(column.replace(' ', ''))
        return newColumns

    @staticmethod
    def __timeShootings(columnString: str, valueToReturn: int) -> List[str]:
        timeValues: List[str] = columnString.split(' ')[:-1]
        assert all(
            list(map(lambda x: x[-1] == 's', timeValues))), "Not all second values"
        timeValuesIsDigit: List[str] = list(map(lambda x: x[:-1], timeValues))

        return timeValuesIsDigit[valueToReturn]

    @staticmethod
    def __decideStarting(orderString: str) -> str:

        if '1' not in orderString and np.all([str(i) in orderString for i in range(2, 6)]):

            orderString: str = orderString.replace('0', '1')
        try:
            if orderString.index('1') == 4:
                startedFrom: str = 'right'
            elif orderString.index('1') == 0:
                startedFrom: str = 'left'
            else:
                startedFrom: str = 'middle'
        except ValueError:
            intOrder = [int(orderChar)
                        for orderChar in orderString if int(orderChar) != 0]
            if len(intOrder) > 1:
                if np.all(np.diff(intOrder) > 0):
                    startedFrom: str = 'left'
                elif np.all(np.diff(intOrder) < 0):
                    startedFrom: str = 'right'
                else:
                    startedFrom: str = 'unknown'
            else:
                startedFrom: str = 'unknown'
        return startedFrom

    def getShootingTable(self) -> Generator[pd.DataFrame, None, None]:
        idAthletes: List[int] = getLoopTimes.getAthletesId(idRace=self.idRace)
        tableHtml: str = self.drvr.find_element(
            By.ID, 'thistable').get_attribute('innerHTML')
        dfShooting: pd.DataFrame = pd.read_html(
            '<table>' + tableHtml + '</table>')[0]
        assert len(dfShooting) == len(
            idAthletes), "Loop dataframe and athlete ids did not match"
        dfShooting: pd.DataFrame = dfShooting.drop(
            columns=['Rank', 'Bib', 'Family\xa0Name', 'Given Name', 'Nation'])
        dfShooting.columns: List[str] = self.__manouverRepeatedColumns(
            dfShooting)
        shootingColumns = list(
            filter(lambda x: 'Shooting' in x, dfShooting.columns))
        nShootings: int = len(shootingColumns)
        for column in shootingColumns:
            dfShooting[f'shootingOrder{column[-1]}']: pd.Series = dfShooting.apply(lambda x: x[column].split(
                ' ')[-1] if isinstance(x[column], str) else None, axis=1)
            dfShooting[f'shooting{column[-1]}StartedFrom']: pd.Series = dfShooting.apply(
                lambda x: self.__decideStarting(x[f'shootingOrder{column[-1]}']) if isinstance(x[f'shootingOrder{column[-1]}'], str) else None, axis=1)
            for target in range(nTargets):
                dfShooting[f'time{column[-1]}Target{target + 1}']: pd.Series = dfShooting.apply(lambda x: self.__timeShootings(
                    x[column], target) if isinstance(x[column], str) else None, axis=1)

            dfShooting: pd.DataFrame = dfShooting.drop(columns=[column])

        for i in range(nShootings):
            filteredDf: pd.DataFrame = dfShooting[list(filter(lambda x: re.search(
                r"\d{1}", x).group() == f'{i + 1}', dfShooting.columns))]
            filteredDf.columns = [column.replace(
                f'{i + 1}', '', 1) for column in filteredDf.columns]
            filteredDf['idRace']: pd.Series = self.idRace

            filteredDf['rangeNumber']: pd.Series = i + 1

            filteredDf['idAthlete'] = idAthletes

            filteredDf = filteredDf.rename(
                columns={'Lane': 'lane', 'Time': 'shootingTime'})

            yield filteredDf
