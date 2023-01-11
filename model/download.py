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

xgboost_model_path = Path("model/xgb.ubj")

if not xgboost_model_path.exists():
    gdown.download(
        "https://drive.google.com/uc?export=download&confirm=pbef&id=1r7HNiONPy_i0aVSb0L5u1z3qcs3d2SRO",
        output=str(xgboost_model_path),
        quiet=False,
    )

rf_model_path = Path("model/rf.sav")

if not rf_model_path.exists():
    gdown.download(
        "https://drive.google.com/uc?export=download&confirm=pbef&id=1FgS40cYfYGZ7ll9TCTSdOdCqi58BxyFc",
        output=str(rf_model_path),
        quiet=False,
    )
