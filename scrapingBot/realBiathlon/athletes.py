import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from realBiathlon.constants import mainUrl
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
from typing import List


class athletes(webdriver.Chrome):
    def __init__(self, driverPath: str = r'/Users/tommaso/Workspace/seleniumDrivers/chromedriver_mac64',
                 teardown: bool = False) -> None:
        self.driverPath = driverPath
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        os.environ['PATH'] += self.driverPath

        super(athletes, self).__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print('Exiting...')
        if self.teardown:
            self.quit()

    def landInRealBiathlon(self) -> None:
        self.get(mainUrl)

    def goToAthletes(self) -> None:

        athlethesButton = self.find_element(
            By.CSS_SELECTOR,
            'a[href = "athletes.html"]')

        athlethesButton.click()

    def selectGender(self, gender: str) -> None:

        assert gender == "W" or gender == "M", 'Gender must be one of M or W'

        genderButton = self.find_element(
            By.ID,
            gender + 'button')

        genderButton.click()

    def clickAthleteField(self) -> None:

        searchFieldWrapper = self.find_element(By.ID,
                                               'rightsearchfield')

        time.sleep(2)

        clickableSpan = searchFieldWrapper.find_element(By.CLASS_NAME,
                                                        'selection')
        # Other element would receive the click: <span class="selection">...</span>

        clickableSpan.click()

    def pressDownArrow(self, nValues: int) -> None:
        counter: int = 0
        while counter < nValues:
            ActionChains(self).key_down(Keys.ARROW_DOWN).perform()
            counter += 1

    def findEntriesDropDown(self) -> List[str]:

        ulElement = self.find_element(By.ID,
                                      'select2-namesdropdown10-results')
        liElements = ulElement.find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        textElements = [element.text for element in liElements]

        return textElements

    def sendAthleteToInput(self, athlete: str) -> None:

        element = self.find_element(
            By.ID, 'rightsearchfield')

        time.sleep(2)

        element2 = element.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Search for athletes"]')

        element2.send_keys(athlete)

    def selectSingleOption(self) -> None:
        self.find_element(By.CSS_SELECTOR, 'li[role="option"]').click()

    def findBirthday(self) -> str:
        divBirthday = self.find_element(By.ID, 'pagesubheaderright')
        birthday = re.findall(r'\d{4}-\d{2}-\d{2}', divBirthday.text)
        return birthday

    def getAlpha2(self) -> str:
        divFlag = self.find_element(By.ID, 'bioflag')
        flagClass = divFlag.find_element(
            By.CSS_SELECTOR, '*').get_attribute('class')
        alpha2 = flagClass.split('-')[-1]
        return alpha2

    def getSpecificAthleteDropdown(self, athlete: str) -> None:
        ulElement = self.find_element(By.ID,
                                      'select2-namesdropdown10-results')
        liElements = ulElement.find_elements(
            By.CSS_SELECTOR, 'li[role="option"]')

        for element in liElements:
            if element.text == athlete:
                element.click()
                break
