from dataCenter.results import results
from typing import Type

year:int = 2022

level = 'world'



with results(teardown=True, level=level) as resultsInstance:
    
    resultsInstance:Type["results"]

    resultsInstance.landInDataCenter()

    resultsInstance.getInsideDataCenter()

    resultsInstance.acceptCookies()

    for year in range(1957, 2020)[::-1]:

        season=f'{year}/{year+1}'

        resultsInstance.selectYear(year=year)

        resultsInstance.selectLevel()

        resultsInstance.getStagesToMySql(season=season)




 