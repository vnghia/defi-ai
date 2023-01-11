from pathlib import Path

import gdown

price_model_path = Path("model/price_catboost.cbm")
stock_model_path = Path("model/stock_catboost.cbm")

if not price_model_path.exists():
    gdown.download(
        "https://drive.google.com/uc?export=download&confirm=pbef&id=17pKxiOP0XJ8AuVw6AMxVUlCXACQRFeR9",
        output=str(price_model_path),
        quiet=False,
    )

if not stock_model_path.exists():
    gdown.download(
        "https://drive.google.com/uc?export=download&confirm=pbef&id=1VW6v9MWwUyEPGaBqeLw7NwzVl1o0TngJ",
        output=str(stock_model_path),
        quiet=False,
    )
