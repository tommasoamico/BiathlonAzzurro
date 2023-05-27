from realBiathlon.races import races
import time
import pandas as pd
import numpy as np
from realBiathlon.usefuls import selectSurname
from realBiathlon.constants import genders

with races(teardown=True) as botRace:
    botRace.implicitly_wait(15)
    botRace.landInRealBiathlon()

    botRace.goToRaces()

    botRace.getAllYears()
