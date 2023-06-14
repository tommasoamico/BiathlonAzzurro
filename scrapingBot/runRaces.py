from realBiathlon.races import races
import time
import pandas as pd
import numpy as np
from realBiathlon.usefuls import selectSurname
from realBiathlon.constants import genders
from realBiathlon.mySql import mySqlObject
from typing import List, Type, Generator
from selenium.webdriver.remote.webelement import WebElement
from pprint import pprint


year: int = 2023
level: str = 'IBU'
stageExample: int = 1
raceExample: int = 0
with races(teardown=True, year=year, level=level) as botRace:
    botRace.implicitly_wait(15)
    botRace.landInRealBiathlon()

    botRace.goToRaces()

    time.sleep(.5)

    botRace.selectYear()

    botRace.selectLevel()

    stageRaceDict: dict = botRace.findAllStagesAndRaces()

    stageExample: int = list(stageRaceDict.keys())[stageExample]

    raceExampleId, statusRealBiathlon = stageRaceDict[stageExample][raceExample]

    statusDb: str = botRace.getRaceStatus(raceId=raceExampleId)

    insertStatus: str = botRace.getRaceInsertStatus(raceId=raceExampleId)

    if insertStatus != 'inserted':

        if statusDb != statusRealBiathlon:
            botRace.adjustStatus(
                raceId=raceExampleId, statusRealBiathlon=statusRealBiathlon)

        ######################
        # Insert Race Result #
        ######################
        '''
        if statusRealBiathlon == 'Final':

            botRace.clickRace(stagePosition=1, racePosition=0)

            raceResults = botRace.getRaceResult(raceId=145)

            dfResults = raceResults.getResultsTable()

            botRace.insertIntoTableDf(tableName='raceResults', df=dfResults)
        '''
        botRace.clickRace(stagePosition=1, racePosition=0)

        clickableSections: List[str] = botRace.getAllClickableSections()

        if 'Loop Times' in clickableSections:
            loopHandler: Type = botRace.getLoopTimes(
                raceId=raceExampleId)

            loopHandler.goToLoops()

            loopElements, loopTexts = loopHandler.getAllLoops()

            for i, (loopElement, loopText) in enumerate(zip(loopElements, loopTexts)):

                loopHandler.clickLoop(loopElement)

                time.sleep(.5)

                if i == 0:
                    loopHandler.switchToAbsoluteTimes()

                loopDf: pd.DataFrame = loopHandler.getLoopTable(
                    loopNumber=loopText)

                ######################
                # Insert Loop Result #
                ######################
                # botRace.insertIntoTableDf(tableName='loopsTable', df=loopDf)

        if 'Shooting' in clickableSections:

            shootingHandler: Type = botRace.getShootingResults(
                raceId=raceExampleId)

            shootingHandler.goToShooting()

            generatorDf: Generator[pd.DataFrame, None,
                                   None] = shootingHandler.getShootingTable()

            ###########################
            # Insert Shootings Result #
            ###########################
            # for df in generatorDf:
            #   botRace.insertIntoTableDf(tableName='shooting', df=df)

        if 'Analysis' in clickableSections:

            analysisHandler: Type = botRace.getAnalysis(raceId=raceExampleId)

            analysisHandler.goToAnalysis()

            time.sleep(.5)

            dropdownElement, textOptions = analysisHandler.getAllAnalysisOptions()

            allAnalysisDf: List[pd.DataFrame] = []
            for dropdown, text in zip(dropdownElement[1:], textOptions[1:-2]):
                analysisHandler.goToAnalysisSection(text)
                time.sleep(1)
                analysisDf: pd.DataFrame = analysisHandler.getAnalysisTable()
                allAnalysisDf.append(analysisDf)
