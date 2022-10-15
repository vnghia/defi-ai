# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pandas as pd
from defi_ai.type import SQLSession
from sqlalchemy.sql.selectable import Select


def execute_to_df(session: SQLSession, statement: Select):
    rows = session.execute(statement).all()
    df = pd.DataFrame(
        [row._mapping for row in rows],
        columns=[c.name for c in statement.selected_columns],
    )
    return df
