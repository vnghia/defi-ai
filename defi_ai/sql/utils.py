# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pandas as pd
from defi_ai.type import City, HotelBrand, HotelGroup, Language, SQLSession
from sqlalchemy.sql.selectable import Select


def execute_to_df(
    session: SQLSession,
    statement: Select,
    convert_category: bool = True,
    convert_enum: bool = False,
):
    rows = session.execute(statement).all()
    df = pd.DataFrame(
        [row._mapping for row in rows],
        columns=[str(c.name) for c in statement.selected_columns],
    )
    if convert_category:
        for c in ["language", "city", "group", "brand", "children_policy"]:
            if c in df.columns:
                df[c] = df[c].astype("category")
    if convert_enum:
        for c, e in zip(
            ["language", "city", "group", "brand", "children_policy"],
            [Language, City, HotelGroup, HotelBrand],
        ):
            if c in df.columns:
                df[c] = df[c].apply(lambda x: e(x).name)
    return df
