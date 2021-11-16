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

from nextres.database.models.user import User
from nextres.database.util import db

from enum import Enum

class GuestListType(Enum):
    Desk = 1
    Express = 2

class Guest(db.Model):
    __tablename__ = 'guests'
    host_kerberos = db.Column(db.String(8), db.ForeignKey(User.kerberos), primary_key=True)
    kerberos = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    list_type = db.Column(db.Enum(GuestListType), nullable=False)
