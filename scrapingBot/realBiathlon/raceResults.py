from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Union
import pandas as pd
from pprint import pprint
from realBiathlon.constants import specialCases
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from realBiathlon.mySql import mySqlObject


class retrieveRaceResults:
    def __init__(self, driver: WebDriver) -> None:
        self.drvr = driver

    def __findBirthday(self) -> List[str]:
        divBirthday: WebElement = self.drvr.find_element(
            By.ID, 'pagesubheaderright')
        birthday: List[str] = re.findall(
            r'\d{4}-\d{2}-\d{2}', divBirthday.text)
        return birthday

    @staticmethod
    def __idQuery(firstName: str, lastName: str, nation: str, birthday: str) -> int:
        assert len(
            nation) == 3, "Nation in the Athlete table is in the alpha3 format"
        if birthday == '':
            query: str = f'SELECT idAthlete FROM Athlete WHERE firstName = "{firstName}" AND lastName = "{lastName}" AND nationAlpha3 = "{nation}" AND birthday is null;'
        else:
            query = f'SELECT idAthlete FROM Athlete WHERE firstName = "{firstName}" AND lastName = "{lastName}" AND nationAlpha3 = "{nation}" AND birthday = "{birthday}";'
        with mySqlObject() as connection:
            connection.useDatabase('biathlon')
            result = connection.executeAndFetch(query)
        # assert len(result) == 1, 'The query result was not unique'
        return result

    def __getAthleteIds(self, table: WebElement) -> None:
        tableWrapper: WebElement = table.find_element(By.TAG_NAME, 'tbody')

        time.sleep(1.5)
        firstNamesElements: List[WebElement] = tableWrapper.find_elements(
            By.CSS_SELECTOR, 'td[data-th="givenName"]')
        firstNames: List[str] = list(map(lambda x: x.text, firstNamesElements))
        lastNamesElements: List[WebElement] = tableWrapper.find_elements(
            By.CSS_SELECTOR, 'td[data-th="familyName"]')
        lastNames: List[str] = list(
            map(lambda x: x.text.upper(), lastNamesElements))
        nationElements: List[WebElement] = tableWrapper.find_elements(
            By.CSS_SELECTOR, 'td[data-th="nat"]')
        nations: List[str] = list(map(lambda x: x.text, nationElements))
        linkBirthdays: list[WebElement] = tableWrapper.find_elements(
            By.TAG_NAME, 'a')
        assert len(linkBirthdays) == len(
            lastNames), "Maybe not all athletes have a link?"
        allAthleteIds: List[str] = [''] * len(linkBirthdays)
        for i, link in enumerate(linkBirthdays):
            self.drvr.get(link.get_attribute('href'))
            time.sleep(1)
            birthdayFindAll: List[str] = self.__findBirthday()
            if len(birthdayFindAll) == 0:
                birthday: str = ''
            else:
                birthday: str = birthdayFindAll[0]
            self.drvr.back()

            time.sleep(.5)
            queryResult = self.__idQuery(
                firstName=firstNames[i], lastName=lastNames[i], nation=nations[i], birthday=birthday)
            allAthleteIds[i] = queryResult
            print(firstNames[i], lastNames[i],
                  birthday, nations[i], queryResult)
        print(allAthleteIds)

        # linkhtml = links.get_attribute('href')
        # self.drvr.get(linkhtml)

        # print(rows)

        # exampleRow.click()

    def getResultsTable(self) -> List[List[Union[str, int]]]:
        table: WebElement = self.drvr.find_element(
            By.CSS_SELECTOR, 'table[id = "thistable"]')
        df: pd.DataFrame = pd.read_html(
            '<table>' + table.get_attribute('innerHTML') + '</table>')[0]

        df['Family\xa0Name'] = df.apply(
            lambda x: x['Family\xa0Name'].upper(), axis=1)
        df['fullName'] = df.apply(
            lambda x: x["Given Name"] + ' ' + x["Family\xa0Name"], axis=1)
        self.__getAthleteIds(table=table)
