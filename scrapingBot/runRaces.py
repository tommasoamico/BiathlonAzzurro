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
from functools import reduce
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from realBiathlon.analysis import analysisHandle
    from realBiathlon.analysisRelay import analysisHandleRelay
    from realBiathlon.splitTimes import splitTimesHandle
    from realBiathlon.splitTimesRelay import splitTimesHandleRelay
    from realBiathlon.metadata import metadataHandle
    from realBiathlon.metadataRelay import metadataHandleRelay
    from realBiathlon.raceResults import retrieveRaceResults
    from realBiathlon.loopTimesRelay import getLoopTimesRelay
    from realBiathlon.shooting import getShooting
    from realBiathlon.shootingRelay import getShootingRelay

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

################################
# Remember to retrieve race km #
################################

###############################################################################
# Remember to make got a static method so that it can be reused across modules #
###############################################################################

###############################################################
# Make the read table procedure reproducable and reproduce it #
###############################################################

year: int = 2023
level: str = 'World'


with races(teardown=True, year=year, level=level) as botRace:
    botRace.implicitly_wait(15)

    botRace.landInRealBiathlon()

    botRace.goToRaces()

    time.sleep(.5)

    botRace.selectYear()

    botRace.selectLevel()

    stageRaceDict: dict = botRace.findAllStagesAndRaces()

    logging.info("Starting bot...")

    for indexStage, stageId in enumerate(stageRaceDict.keys()):
        logging.debug(f'Entered handling of stage with id: {stageId}')
        #
        # raceId, statusRealBiathlon = stageRaceDict[stageId][raceExample]
        for indexRace, (raceId, statusRealBiathlon) in enumerate(stageRaceDict[stageId]):
            logging.debug(f'Entered handling of race with id: {raceId}')
            logging.debug(f'Race biathlon\'s status is {statusRealBiathlon}')
            # print(stageRaceDict[stageId])

            # stageExampleId: int = list(stageRaceDict.keys())[stageExample]

            # raceExampleId, statusRealBiathlon = stageRaceDict[stageExampleId][raceExample]

            generalCategory: str = botRace.getGeneraCategory(raceId=raceId)

            assert generalCategory in [
                "Non-Team", "Team"], "General category mus be either Team or Non-Team"

            statusDb: str = botRace.getRaceStatus(raceId=raceId)

            insertStatus: str = botRace.getRaceInsertStatus(raceId=raceId)

            logging.debug(
                f'The race \'s status of the data base is {statusDb}')
            logging.debug(f'Insert status is {insertStatus}')

            if insertStatus != 'inserted':

                if statusDb != statusRealBiathlon:
                    botRace.adjustStatus(
                        raceId=raceId, statusRealBiathlon=statusRealBiathlon)

                ######################
                # Insert Race Result #
                ######################

                if statusRealBiathlon == 'Final':

                    if generalCategory == 'Non-Team':

                        logging.debug(
                            'Entered raceResults for Non-Team category')

                        botRace.clickRace(stagePosition=indexStage,
                                          racePosition=indexRace)

                        raceResults = botRace.getRaceResult(raceId=raceId)

                        dfResults = raceResults.getResultsTable()

                        ######################
                        # Insert Race Result #
                        ######################

                        botRace.insertIntoTableDf(
                            tableName='raceResults', df=dfResults)

                    if generalCategory == 'Team':

                        logging.debug('Entered raceResults for Team category')

                        botRace.clickRace(stagePosition=indexStage,
                                          racePosition=indexRace)

                        raceResults: Type["retrieveRaceResults"] = botRace.getRaceResult(
                            raceId=raceId)

                        time.sleep(.5)

                        dfResultsTeam: pd.DataFrame = raceResults.getResultsTableTeam()

                        raceResultsNationDf: pd.DataFrame = raceResults.getResultsNationsTeam(
                            df=dfResultsTeam)

                        ###################################
                        # Insert Nation Relay Race Result #
                        ###################################

                        botRace.insertIntoTableDf(
                            tableName='raceResultsRelayNation', df=raceResultsNationDf)

                        raceResultsAthletesDf: pd.DataFrame = raceResults.getResultsAthletesTeam(
                            df=dfResultsTeam)

                        ###################################
                        # Insert Athlete Relay Race Result #
                        ###################################

                        botRace.insertIntoTableDf(
                            tableName='raceResultsRelayAthletes', df=raceResultsAthletesDf)

                    clickableSections: List[str] = botRace.getAllClickableSections(
                    )

                    if 'Loop Times' in clickableSections:

                        logging.info('loop Times is in clickable sections')

                        if generalCategory == 'Non-Team':

                            logging.debug(
                                'Entered Loop Times for Non-Team category')

                            loopHandler: Type = botRace.getLoopTimes(
                                raceId=raceId)

                            loopHandler.goToLoops()

                            loopElements, loopTexts = loopHandler.getAllLoops()

                            for i, (loopElement, loopText) in enumerate(zip(loopElements, loopTexts)):
                                time.sleep(1)

                                loopHandler.clickElement(loopElement)

                                time.sleep(.5)

                                if i == 0:
                                    loopHandler.switchToAbsoluteTimes()

                                loopDf: pd.DataFrame = loopHandler.getLoopTable(
                                    loopNumber=loopText)

                                ######################
                                # Insert Loop Result #
                                ######################
                                botRace.insertIntoTableDf(
                                    tableName='loopsTable', df=loopDf)

                        if generalCategory == 'Team':
                            logging.debug(
                                'Entered Loop Times for Team category')

                            loopHandler: Type["getLoopTimesRelay"] = botRace.getLoopTimesRelay(
                                raceId=raceId)
                            time.sleep(2)
                            ###########################################
                            # Insert explicit wait, clickable element #
                            ###########################################
                            loopHandler.goToLoops()

                            loopElements, loopTexts = loopHandler.getAllLoops()

                            athleteElements, athleteTexts = loopHandler.getAllAthleteFields()

                            for i, (loopElement, loopText) in enumerate(zip(loopElements, loopTexts)):
                                if i == 0:
                                    loopHandler.switchToAbsoluteTimes()
                                for j, (athleteElement, athleteText) in enumerate(zip(athleteElements, athleteTexts)):

                                    time.sleep(1)

                                    loopHandler.clickElement(loopElement)

                                    loopHandler.clickElement(athleteElement)

                                    dfAthlete: pd.DataFrame = loopHandler.getLoopTableRelay(
                                        athleteNumber=athleteText, loopNumber=loopText)

                                    ############################
                                    # Insert Loop Result Relay #
                                    ############################

                                    botRace.insertIntoTableDf(
                                        tableName='loopsTableRelay', df=dfAthlete)

                    if 'Shooting' in clickableSections:

                        logging.info('Shooting is in clickable sections')

                        if generalCategory == 'Non-Team':

                            logging.debug(
                                'Entered shooting for Non-Team category')

                            shootingHandler: Type["getShooting"] = botRace.getShootingResults(
                                raceId=raceId)

                            time.sleep(1)

                            shootingHandler.goToShooting()

                            generatorDf: Generator[pd.DataFrame, None,
                                                   None] = shootingHandler.getShootingTable()

                            ###########################
                            # Insert Shootings Result #
                            ###########################
                            for df in generatorDf:
                                botRace.insertIntoTableDf(
                                    tableName='shooting', df=df)

                        if generalCategory == 'Team':

                            logging.debug(
                                'Entered Shooting for Team category')

                            shootingHandlerRelay: Type["getShootingRelay"] = botRace.getShootingResultsRelay(
                                raceId=raceId)

                            time.sleep(1)

                            shootingHandlerRelay.goToShooting()

                            generatorDf: Generator[pd.DataFrame, None,
                                                   None] = shootingHandlerRelay.getShootingTableRelay()

                            ################################
                            # Insert Shootings Relay Result #
                            #################################
                            for df in generatorDf:
                                botRace.insertIntoTableDf(
                                    tableName='shooting', df=df)

                    if 'Analysis' in clickableSections:

                        logging.info('Analysis is in clickable sections')

                        if generalCategory == 'Non-Team':

                            logging.debug(
                                'Entered Analysis for Non-Team category')

                            analysisHandler: Type["analysisHandle"] = botRace.getAnalysis(
                                raceId=raceId)

                            analysisHandler.goToAnalysis()

                            time.sleep(.5)

                            finalAnalysisDf: pd.DataFrame = analysisHandler.getAnalysisFinalTable()

                            ##########################
                            # Insert Analysis Result #
                            ##########################
                            # botRace.insertIntoTableDf(
                            #   tableName='analysis', df=finalAnalysisDf)
                        if generalCategory == 'Team':

                            logging.debug('Entered Analysis for Team category')

                            analysisHandlerRelay: Type["analysisHandle"] = botRace.getAnalysisRelay(
                                raceId=raceId)

                            analysisHandlerRelay.goToAnalysis()

                            finalAnalysisDfRelay: pd.DataFrame = analysisHandlerRelay.getAnalysisFinalTableRelay()

                            ################################
                            # Insert Analysis Relay Result #
                            ################################
                            botRace.insertIntoTableDf(
                                tableName='analysisRelay', df=finalAnalysisDfRelay)

                    if 'Split Times' in clickableSections:

                        logging.info('Split Times is in clickable section')

                        if generalCategory == 'Non-Team':

                            logging.debug(
                                'Entered Split Times for Non-Team category')

                            splitTimesHandler: "splitTimesHandle" = botRace.getSplitTimes(
                                raceId=raceId)
                            splitTimesHandler.goToSplitTimes()

                            splitTimesDf: pd.DataFrame = splitTimesHandler.getSplitTimesTables()

                            ##########################
                            # Insert Split Times     #
                            ##########################

                            botRace.insertIntoTableDf(
                                tableName='splitTimes', df=splitTimesDf)
                        if generalCategory == 'Team':

                            logging.debug(
                                'Entered Split Times for Team category')

                            splitTimesHandlerRelay: "splitTimesHandleRelay" = botRace.getSplitTimesRelay(
                                raceId=raceId)

                            splitTimesHandlerRelay.goToSplitTimes()

                            splitTimesDfRelay: pd.DataFrame = splitTimesHandlerRelay.getSplitTimesRelayTable()

                            ############################
                            # Insert Split Times Relay #
                            ############################

                            botRace.insertIntoTableDf(
                                tableName='splitTimes', df=splitTimesDfRelay)

                    if 'Metadata' in clickableSections:

                        logging.info('Metadata is in clickable sections')

                        metadataHandler: "metadataHandle" = botRace.getMetadata(
                            raceId=raceId)

                        metadataHandler.goToMetadata()

                        metadataDf: pd.DataFrame = metadataHandler.getMetadataTable()

                        ##########################
                        # Insert Metadata        #
                        ##########################

                        botRace.insertIntoTableDf(
                            tableName='metadata', df=metadataDf)

            botRace.setInstertState(raceId=raceId)
