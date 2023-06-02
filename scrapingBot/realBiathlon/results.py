import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from realBiathlon.constants import mainUrl
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from typing import List


class results(webdriver.Chrome):
    def __init__(self, driverPath: str = r'/Users/tommaso/Workspace/seleniumDrivers/chromedriver_mac64',
                 teardown: bool = False) -> None:
        self.driverPath: str = driverPath
        self.teardown: bool = teardown
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        os.environ['PATH'] += self.driverPath

        super(results, self).__init__(options=options)
        self.implicitly_wait(15)
        self.maximize_window()
