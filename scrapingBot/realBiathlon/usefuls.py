from typing import Iterable, List, Tuple
import csv
import numpy as np
import pandas as pd


def selectSurname(athlete: str) -> str:
    return athlete.split(' ')[-1]


def tail(someIterable: Iterable) -> Iterable:
    return someIterable[1:]


def getCsvHeader(path: str) -> List[str]:
    with open(path, 'r') as file:
        # Create a csv.reader object
        reader: csv.reader = csv.reader(file)

        # Retrieve the header row
        header: List[str] = next(reader)

        return header


def selectNameSurname(fullName: str) -> Tuple[str]:
    mask = np.array(list(map(lambda x: x.isupper(), fullName.split(' '))))
    arrayFullName = np.array(fullName.split(' '))

    firstName = ' '.join(arrayFullName[~mask])
    lastName = ' '.join(arrayFullName[~mask])
    return firstName, lastName


def makeColumnTime(columnName: str, df: pd.DataFrame) -> pd.Series:
    newColumn: pd.Series = df[columnName].apply(
        lambda x: '00:' + x if isinstance(x, str) and x.count(':') == 1 else x)
    return newColumn


def makeStringCamelCase(string: str) -> str:
    string = string.replace('%', 'Percentage')
    splittedString: List[str] = string.split(' ')
    dromedaryWord: str = splittedString[0]
    camelWords: List[str] = splittedString[1:]
    if dromedaryWord[0].isupper():
        splittedString[0] = dromedaryWord[0].lower() + dromedaryWord[1:]
    for i, camelWord in enumerate(camelWords):
        if camelWord[0].islower():
            splittedString[i + 1] = camelWord.capitalize()
    finalColumnName = ''.join(splittedString)
    return finalColumnName
