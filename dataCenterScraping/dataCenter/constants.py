from typing import Dict, List

datacenterUrl:str = 'https://www.biathlonresults.com/#/start'

levelList:List[str] = ['world', 'ibu', 'junior', 'other']

eventParser:Dict[str, List[str]] = \
    {'world':['world cup', 'world championships', 'olympic winter games',
              'world championship', 'world biathlon championship'],
     'ibu':['ibu cup', 'european cup', 'european championships'],
     'junior':['junior cup'],
     'other':['summer biathlon world championships']}


eventCorrespondances:Dict[str, str] = \
    {'world championship':'world championships',
     'world biathlon championship':'world championships'}
