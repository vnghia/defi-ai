import enum

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
    "bulgarian",
    "cypriot",
    "croatian",
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
