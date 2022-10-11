# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta


SQLBase: type[DeclarativeMeta] = declarative_base()
