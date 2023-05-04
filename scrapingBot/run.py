from realBiathlon.athletes import athletes


with athletes(teardown=False) as botAth:

    botAth.landInRealBiathlon()

    botAth.goToAthletes()

    # Gender must be a string, either 'M' or 'W'
    botAth.selectGender(gender = 'M')

    botAth.clickAthleteField()

    #botAth.getAthlete()


