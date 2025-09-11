# -*- coding: utf-8 -*-
"""
"""


from mcmodupdater.models import (
    ModFile,
    CurseForgeAPI
)

import re
import json



def check_version_format(
    version: str
) -> bool:
    """
    """
    item = re.findall(r'(\d{1}\.\d+(?:\.\d+){0,2})', version)
    if item:
        if item[0] == version:
            return True
    return False


def load_data(path: str) -> list:
    with open(path, "r") as fl:
        data = fl.readlines()
    return data


def clear_text(
    filename: str,
    filters: list = []
) -> tuple:
    """
    """
    if filters is None:
        filters = []

    filename = filename.strip().lower()

    name_item = [
        re.sub("|".join(filters), "", item)
        for item in re.split(r'-|_|\s', filename, flags=re.IGNORECASE)
        if "." not in item
        if not item.isnumeric()
        if re.sub("|".join(filters), "", item)
    ]

    name_item = " ".join(name_item)

    name_item = re.sub(r'\d+\.\d+\.\d+', '', name_item)

    results = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', name_item)
    return (filename, " ".join(results))


def clear_data(
    data: list,
    custom_filters: list = []
) -> list:
    names = []
    for item in data:
        filename_name = clear_text(filename=item, filters=custom_filters)
        # print(filename_name)
        names.append(filename_name)
    return names


def get_models(data: list) -> None:
    """
    """
    return [
        Mod(
            name=i[1],
            filename=i[0],
            slug=i[1],
            # in_db=,
        ) for i in data
    ]


def get_names_flat(name: str) -> str:
    """
    """
    return "".join(re.findall(r'[a-zA-Z0-9]+', name))
