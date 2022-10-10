import enum

import pandas as pd

cities = [
    "amsterdam",
    "copenhagen",
    "madrid",
    "paris",
    "rome",
    "sofia",
    "valletta",
    "vienna",
    "vilnius",
]

City = enum.Enum("City", cities)

languages = [
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
]

Language = enum.Enum("Language", languages)

df_hotel = pd.read_csv("dataset/features_hotels.csv")

HotelGroup = enum.Enum("HotelGroup", sorted(df_hotel["group"].unique()))
HotelBrand = enum.Enum("HotelBrand", sorted(df_hotel["brand"].unique()))
