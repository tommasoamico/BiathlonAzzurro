import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from realBiathlon.constants import mainUrl


class athletes(webdriver.Chrome):
    def __init__(self, driverPath : str = r'/Users/tommaso/Workspace/seleniumDrivers/chromedriver_mac64',\
                 teardown : bool= False) -> None:
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

    def selectGender(self, gender:str) -> None:

        assert gender == "W" or gender == "M", 'Gender must be one of M or W'

        genderButton = self.find_element(
            By.ID,
            gender + 'button')

        genderButton.click()

    def clickAthleteField(self) -> None:

        
        athletesField1 = self.find_element(
            By.CSS_SELECTOR,
            'input[aria-controls="select2-namesdropdown10-results"]')
        
        athletesField1.send_keys('a')
        


    def getAthlete(self) -> None:
        athlete  = self.find_element(
            By.CSS_SELECTOR,
            'input[aria-controls="select2-namesdropdown10-results"]')
        

        athlete.find_element(By.CSS_SELECTOR ,'*')

        for ath in athlete:
            print(ath.get_attribute('innerHTML'))




        
