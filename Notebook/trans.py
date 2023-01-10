import numpy as np
import pandas as pd
import os

path = os.path.abspath(os.getcwd())
hotel = pd.read_csv(path + "/data/hotel.csv")

sample = pd.read_csv(path + "/data/sample.csv")
sample["mobile"] = sample["mobile"].astype(int)
sample = sample.drop(["scrape_request_id"], axis=1)
sample["request_id"] = sample["order_requests"]
sample = sample.drop(["order_requests"], axis=1)
sample = sample.drop(["city"], axis=1)
df = pd.read_csv(path + "/data/dataset.csv")
sample = sample.join(hotel.set_index("id"), on="hotel_id", validate="m:1")


cols = ["city", "group", "brand", "language"]
cname = [
    [
        "paris",
        "copenhagen",
        "amsterdam",
        "rome",
        "madrid",
        "vienna",
        "vilnius",
        "sofia",
        "valletta",
    ],
    [
        "Independant",
        "Accar Hotels",
        "Boss Western",
        "Yin Yang",
        "Morriott International",
        "Chillton Worldwide",
    ],
    [
        "Independant",
        "Boss Western",
        "J.Halliday Inn",
        "Royal Lotus",
        "Safitel",
        "Corlton",
        "Marcure",
        "Ardisson",
        "8 Premium",
        "Morriot",
        "Ibas",
        "Quadrupletree",
        "Navatel",
        "Chill Garden Inn",
        "CourtYord",
        "Tripletree",
    ],
    [
        "hungarian",
        "french",
        "finnish",
        "austrian",
        "estonian",
        "bulgarian",
        "danish",
        "swedish",
        "slovakian",
        "romanian",
        "irish",
        "maltese",
        "italian",
        "greek",
        "belgian",
        "dutch",
        "cypriot",
        "lithuanian",
        "polish",
        "latvian",
        "czech",
        "luxembourgish",
        "german",
        "croatian",
        "portuguese",
        "slovene",
        "spanish",
    ],
]

for i, col in enumerate(cols):
    df[col].replace(
        cname[i],
        (np.linspace(1, len(cname[i]), len(cname[i]))).astype(int),
        inplace=True,
    )
    sample[col].replace(
        cname[i],
        (np.linspace(1, len(cname[i]), len(cname[i]))).astype(int),
        inplace=True,
    )
df = df.drop(["Unnamed: 0"], axis=1)
# print(df.columns)
sample.to_csv(path + "/data/temp/ready_sample.csv", index=False)
df.to_csv(path + "/data/temp/ready_data.csv", index=False)
