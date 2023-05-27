from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from realBiathlon.constants import mainUrl
import os
import time


class races(webdriver.Chrome):
    def __init__(self, driverPath: str = r'/Users/tommaso/Workspace/seleniumDrivers/chromedriver_mac64',
                 teardown: bool = False) -> None:
        self.driverPath = driverPath
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        os.environ['PATH'] += self.driverPath

        super(races, self).__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print('Exiting...')
        if self.teardown:
            self.quit()

    def landInRealBiathlon(self) -> None:
        self.get(mainUrl)

    def goToRaces(self) -> None:
        raceButton = self.find_element(
            By.CSS_SELECTOR,
            'a[href = "races.html"]')

        raceButton.click()

    def __getAllYears(self) -> List[str]:
        time.sleep(1)
        yearDropdown = self.find_element(
            By.ID,
            'select2-years-container')
        yearDropdown.click()
