from realBiathlon.athletes import athletes
import time
import pandas as pd
import numpy as np
from realBiathlon.usefuls import selectSurname
from realBiathlon.constants import genders
for gender in genders:
    with athletes(teardown=True) as botAth:
        botAth.implicitly_wait(15)
        botAth.landInRealBiathlon()

        botAth.goToAthletes()

        # Gender must be a string, either 'M' or 'W'
        botAth.selectGender(gender=gender)

        botAth.clickAthleteField()

        # 7000 is a value that allow to scroll the dropdown all the way down
        botAth.pressDownArrow(nValues=7000)  # 7000

        time.sleep(1)

        athletesNames = botAth.findEntriesDropDown()

        # For the mometn, for testing purposes
        athletesNames = ['Lene Berg AADLANDSVIK'] + athletesNames

        currentDf = pd.read_csv('athletesTable.csv')
        currentAthletes = list(currentDf['athlete'])

        alpha2Fail = []
        for athlete in athletesNames:
            if athlete in currentAthletes:
                pass
            else:
                time.sleep(1)
                botAth.goToAthletes()
                time.sleep(1)
                try:
                    botAth.sendAthleteToInput(athlete)
                    botAth.selectSingleOption()
                except:
                    time.sleep(1)
                    botAth.goToAthletes()
                    botAth.sendAthleteToInput(selectSurname(athlete))
                    botAth.getSpecificAthleteDropdown(athlete)
                time.sleep(1)
                birthday = botAth.findBirthday()
                if len(birthday) == 0:
                    birthday = np.nan
                else:
                    birthday = birthday[0]

                try:
                    alpha2 = botAth.getAlpha2()
                    if len(alpha2) == 0:
                        alpha2 = np.nan
                except:
                    alpha2 = np.nan

                alpha2String = '' if isinstance(alpha2, float) else alpha2
                birthdayString = '' if isinstance(
                    birthday, float) else birthday
                with open('athletesTable.csv', mode='a') as f:
                    f.write(
                        f'{athlete},{birthdayString},{alpha2String},{gender}\n')
                if alpha2 == np.nan:
                    with open('alpha2Fail2.txt', mode='a') as f:
                        f.write('\n' + athlete)

        time.sleep(2)
        # botAth.getAthlete()
