from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typeguard import typechecked
from typing import List, Type, Optional, Any, Tuple
from dataCenter.constants import datacenterUrl, levelList, eventParser
from dataCenter.utilityFunctions import parseVenueAndCountry, parseStartEndDate, retrieveVenueId, parseCompetition
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
from selenium.common.exceptions import TimeoutException
from datetime import date
import re
from selenium.webdriver.common.action_chains import ActionChains 
import numpy as np
from dataCenter.mySql import mySqlObject
import logging


logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class results(webdriver.Chrome):
    all: List[Type] = []

    @typechecked
    def __init__(self, level:str, driverPath: str = r'/Users/au753849/OneDrive - Aarhus universitet/sharedWorkspace/seleniumDrivers/chrome-mac-arm64',
                    teardown: bool = False) -> None:
        
        self.driverPath:str = driverPath
        self.teardown:bool = teardown
        self.level:str = level

        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        os.environ['PATH'] += self.driverPath

        super(results, self).__init__(options=options)
        self.implicitly_wait(15)
        

    @typechecked
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print('Exiting...')
        if self.teardown:
            self.quit()

    @typechecked
    def landInDataCenter(self) -> None:
        self.get(datacenterUrl)

    @typechecked    
    def getInsideDataCenter(self) -> None:

        loginButton:WebElement = WebDriverWait(self, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='CONTINUE WITHOUT REGISTRATION']")))

        loginButton.click()

    @typechecked
    def acceptCookies(self) -> None:

        try:
            okButton:WebElement = WebDriverWait(self, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()='OK']")))
            
            okButton.click()

        except TimeoutException:
            pass


    def __getCurrentSeason(self) -> int:
        seasonItem:WebElement = self.find_element(
            By.CSS_SELECTOR,
            'prevnext-selector[displayfield = "Description"]')
        
        textHtml:str = seasonItem.get_attribute('innerHTML')

        yearWebObject:re.Match = re.search('\d{4}/\d{4}', textHtml)

        if yearWebObject:
            yearWeb:str = yearWebObject.group().split('/')[0]
        else:
            raise ValueError('Current year not found')
        
        return int(yearWeb)
    
    
    @typechecked
    def selectYear(self, year:int) -> None:
        '''
        The year must be a 4 digit number. If the input is 2023 the season will be 2023/2024
        '''

        assert len(str(year)) == 4, "The year must have 4 digits"

        currentDate:date = date.today()

        currentYear:int = currentDate.year

        assert year >= 1957 and year <= currentYear, f'The year can be chosen between {1957} and {currentYear}'

        currentSeason:int = self.__getCurrentSeason()

        if year < currentSeason:

            while currentSeason != year:

                leftArrow:WebElement = WebDriverWait(self, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'competition-schedule-header[au-target-id="263"]')))
            
            
                leftArrow.click()

                currentSeason:int = self.__getCurrentSeason()

            
            

        elif year > currentSeason:
            raise NotImplementedError('At the current state, accessing years the current season has not been implemented yet')

        else:
            pass


    @typechecked
    def selectLevel(self) -> None:

        assert self.level in levelList, f'Level must be one of {levelList}'

        levelIdx:int = levelList.index(self.level)

        levelTab:WebElement = self.find_element(By.CSS_SELECTOR, 'ul[class="nav nav-tabs"]')

        correctLevel:WebElement = levelTab.find_elements(By.CSS_SELECTOR, f'a[role="button"]')[levelIdx]
        
        correctlevel:WebElement = WebDriverWait(self, 10).until(
                    EC.element_to_be_clickable(correctLevel))

        correctlevel.click()

    
    @typechecked
    def getStagesToMySql(self, season:str) -> Any:
        
        stagesPanel:WebElement = self.find_element(By.CSS_SELECTOR, 'div[class="panel-group"]')

        stagesTables:List[WebElement] = stagesPanel.find_elements(By.CSS_SELECTOR, 'a[role="button"]')

        for stage in stagesTables:
            
            stage:WebElement

            stageEntries:List[WebElement] = stage.find_elements(By.TAG_NAME, 'td')

            stageDates:str = stageEntries[0].text + stageEntries[2].text

            venueAndCountry:str = stageEntries[3].text

            competition:str = stageEntries[1].text.lower()

            venue, ioc = parseVenueAndCountry(input=venueAndCountry)            

            startDate, endDate = parseStartEndDate(input=stageDates)

            competitionParsed:str = parseCompetition(competition=competition, level=self.level)
            
            with mySqlObject() as mysqlC:

                mysqlC.useDatabase('biathlonAzzurro')
                

                if ioc.count('/') == 1:

                    assert venue.count('/') == 1, "There were 2 countries found but not 2 venues"

                    ioc1:str = ioc.split('/')[0]

                    ioc2:str = ioc.split('/')[1]

                    venue1:str = venue.split('/')[0]

                    venue2:str = venue.split('/')[1]

                    countryResultQuery1:List[Tuple[str]] = mysqlC.executeAndFetch(command=
                                 f'SELECT countryName FROM countries WHERE ioc="{ioc1}"')
                
                    assert len(countryResultQuery1) == 1, "The country name query did not provide a unique result"

                    countryResultQuery2:List[Tuple[str]] = mysqlC.executeAndFetch(command=
                                 f'SELECT countryName FROM countries WHERE ioc="{ioc2}"')
                
                    assert len(countryResultQuery2) == 1, "The country name query did not provide a unique result"

                    country1:str = countryResultQuery1[0][0]

                    country2:str = countryResultQuery2[0][0]      

                    idVenue1:int = retrieveVenueId(venue=venue1, 
                                                   country=country1)

                    idVenue2:int = retrieveVenueId(venue=venue2,
                                                   country=country2)

                elif ioc.count('/') == 0:

                    countryResultQuery:List[Tuple[str]] = mysqlC.executeAndFetch(command=
                                 f'SELECT countryName FROM countries WHERE ioc="{ioc}"')
                
                    assert len(countryResultQuery) == 1, "The country name query did not provide a unique result"

                    country:str = countryResultQuery[0][0] 
                    
                    idVenue1:int = retrieveVenueId(venue=venue,
                                                   country=country)

                    idVenue2:None = None

                else:
                    raise ValueError('More than 1 "/" was found in the country')

                


                

                

                stageQuery:List[Tuple[int]] = mysqlC.executeAndFetch(command=
                    f"""
                    SELECT stageId FROM stages
                    WHERE
                    startDate="{startDate}" AND
                    endDate="{endDate}" AND
                    venueId="{idVenue1}" AND
                    venueId2="{idVenue2}" AND
                    level="{self.level}" AND
                    competition="{competitionParsed}" AND
                    season="{season}";
                    """ if idVenue2 is not None else
                    f"""
                    SELECT stageId FROM stages
                    WHERE
                    startDate="{startDate}" AND
                    endDate="{endDate}" AND
                    venueId="{idVenue1}" AND
                    level="{self.level}" AND
                    competition="{competitionParsed}" AND
                    season="{season}";
                    """
                )

                assert len(stageQuery) <= 1, "stage data matched multiple stages"

                if len(stageQuery) == 1:
                    print("stage already present in the database")

                    logging.info("stage already present in the database")

                else:
                    
                    logging.info(f"inserting stage into database, year={season}")

                    mysqlC.executeAndCommit(
                    command=f'INSERT INTO stages (startDate, endDate, venueId, venueId2, level, competition, season) VALUES ("{startDate}", "{endDate}", "{idVenue1}", "{idVenue2}", "{self.level}", "{competitionParsed}", "{season}");' if idVenue2 is not None else
                    f'INSERT INTO stages (startDate, endDate, venueId, level, competition, season) VALUES ("{startDate}", "{endDate}", "{idVenue1}", "{self.level}", "{competitionParsed}", "{season}");'

                    )
            

            







            

            


            









        
        
        


        
