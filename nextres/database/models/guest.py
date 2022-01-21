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

__all__ = ['Guest', 'GuestListType']

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, String

from nextres.database.models.user import User
from nextres.database.util import Base

from enum import Enum

class GuestListType(Enum):
    Desk = 1
    Express = 2

class Guest(Base):
    __tablename__ = 'guests'
    host_kerberos = Column(String(8), ForeignKey(User.kerberos, ondelete='cascade', onupdate='cascade'), primary_key=True)
    kerberos = Column(String(8), primary_key=True)
    name = Column(String(255), nullable=False)
    list_type = Column(SQLEnum(GuestListType), nullable=False)
    phone = Column(String(15))
