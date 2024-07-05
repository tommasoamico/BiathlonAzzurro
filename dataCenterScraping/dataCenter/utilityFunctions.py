from parse import parse, Result
from typing import Dict, Tuple, Optional
from typeguard import typechecked
from datetime import datetime
from typing import List
from dataCenter.mySql import mySqlObject
import logging
from dataCenter.constants import eventParser, eventCorrespondances
import numpy as np


logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

@typechecked
def parseVenueAndCountry(input:str) -> Tuple[str, str]:
    
    pattern:str = '{venue} ({ioc})'

    parsingResult:Result = parse(pattern, input)
    
    if parsingResult:

        venue:str = parsingResult['venue'].strip().lower().capitalize()

        ioc:str = parsingResult['ioc'].strip()

        return venue, ioc
    
    else:

        raise ValueError("The venue-and-country string does not match the expected format")
    

@typechecked
def parseStartEndDate(input:str) -> Tuple[datetime, datetime]:

    pattern:str = '{day1} {month1} -{day2} {month2} {year}'

    parsingResult:Result = parse(pattern, input)

    startDate:str = f'{parsingResult["day1"]} {parsingResult["month1"]} {parsingResult["year"]}'

    endDate:str = f'{parsingResult["day2"]} {parsingResult["month2"]} {parsingResult["year"]}'

    startDateObject:datetime = datetime.strptime(startDate, "%d %b %Y")

    endDateObject:datetime = datetime.strptime(endDate, "%d %b %Y")

    return startDateObject, endDateObject

@typechecked
def retrieveVenueId(venue:str, country:str) -> int:

    with mySqlObject() as mysqlC:

        mysqlC.useDatabase('BiathlonAzzurro')
    
        venueIdQueryResult:List[Tuple[int]] = mysqlC.executeAndFetch(command=
                                        f'SELECT id FROM venues WHERE venue="{venue}" AND country="{country}"')
        
        assert len(venueIdQueryResult) <= 1, "The venue Id query gave multiple results"

        if len(venueIdQueryResult) == 0:

            logging.info(f'venue {venue} of {country} is a new venue, inserting it into the venues table...')

            mysqlC.executeAndCommit(command=
                                        f'INSERT INTO venues (venue, country) VALUES ("{venue}", "{country}")')   
            
            venueIdQueryResult:List[Tuple[int]] = mysqlC.executeAndFetch(command=
                            f'SELECT id FROM venues WHERE venue="{venue}" AND country="{country}"')

        else:
            pass

        assert len(venueIdQueryResult) == 1, "The venue Id query did not give an unique result"

        venueId:int = venueIdQueryResult[0][0]

        return venueId
    
@typechecked
def __applyEventCorrespondances(competition:str) -> str:

    try:

        competitionParsed:str = eventCorrespondances[competition]

    except KeyError:

        competitionParsed:str = competition

    return competitionParsed


    

@typechecked
def parseCompetition(competition:str, level:str) -> str:
    
    possibleCompetitions:List[str] = eventParser[level]

    filteredCompetitons:List[str] = list(map(lambda y: __applyEventCorrespondances(y), filter(lambda x: x in competition, possibleCompetitions)))

    assert len(np.unique(filteredCompetitons)) == 1, f'There was not a unique competition found, the competition scraped is {competition}'

    competitionParsed:str = np.unique(filteredCompetitons)[0]

    return competitionParsed
    




