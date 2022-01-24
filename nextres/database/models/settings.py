# spdx-license-identifier: agpl-3.0-only
#
# Copyright (C) 2021 Next Exec
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>

__all__ = ['Settings']

from sqlalchemy import Column, Boolean, Enum as SQLEnum

from nextres.database.util import Base

from enum import Enum

class SettingsIntegrity(Enum):
    Unique = 1

# single-row table of configurations; to add new settings, add additional columns
class Settings(Base):
    __tablename__ = 'settings'
    integrity = Column(SQLEnum(SettingsIntegrity), primary_key=True)
    express_guest_editable = Column(Boolean, nullable=False)
