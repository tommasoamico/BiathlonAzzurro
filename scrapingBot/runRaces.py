from realBiathlon.races import races
import time
import pandas as pd
import numpy as np
from realBiathlon.usefuls import selectSurname
from realBiathlon.constants import genders

year: int = 2023
level: str = 'IBU'
with races(teardown=True, year=year, level=level) as botRace:
    botRace.implicitly_wait(15)
    botRace.landInRealBiathlon()

    botRace.goToRaces()

    botRace.selectYear()

    botRace.selectLevel()

    stageRaceDict: dict = botRace.findAllStagesAndRaces()

    botRace.clickRace(stagePosition=1, racePosition=0)

    raceResults = botRace.getRaceResult()

    raceResults.getResultsTable()
