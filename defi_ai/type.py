# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import enum

from sqlalchemy.engine.base import Engine as SQLEngine  # noqa: F401
from sqlalchemy.orm.session import Session as SQLSession  # noqa: F401

City: enum.IntEnum = enum.IntEnum(
    "City",
    [
        "amsterdam",
        "copenhagen",
        "madrid",
        "paris",
        "rome",
        "sofia",
        "valletta",
        "vienna",
        "vilnius",
    ],
)

Language: enum.IntEnum = enum.IntEnum(
    "Language",
    [
        "austrian",
        "belgian",
        "bulgarian",
        "croatian",
        "cypriot",
        "czech",
        "danish",
        "dutch",
        "estonian",
        "finnish",
        "french",
        "german",
        "greek",
        "hungarian",
        "irish",
        "italian",
        "latvian",
        "lithuanian",
        "luxembourgish",
        "maltese",
        "polish",
        "portuguese",
        "romanian",
        "slovakian",
        "slovene",
        "spanish",
        "swedish",
    ],
)


HotelGroup: enum.IntEnum = enum.IntEnum(
    "HotelGroup",
    [
        "Accar Hotels",
        "Boss Western",
        "Chillton Worldwide",
        "Independant",
        "Morriott International",
        "Yin Yang",
    ],
)

HotelBrand: enum.IntEnum = enum.IntEnum(
    "HotelBrand",
    [
        "8 Premium",
        "Ardisson",
        "Boss Western",
        "Chill Garden Inn",
        "Corlton",
        "CourtYord",
        "Ibas",
        "Independant",
        "J.Halliday Inn",
        "Marcure",
        "Morriot",
        "Navatel",
        "Quadrupletree",
        "Royal Lotus",
        "Safitel",
        "Tripletree",
    ],
)
