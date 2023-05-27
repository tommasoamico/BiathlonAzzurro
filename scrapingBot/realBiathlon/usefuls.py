from typing import Iterable, List, Tuple
import csv
import numpy as np


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
