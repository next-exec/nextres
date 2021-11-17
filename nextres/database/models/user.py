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

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from nextres.database.models.usergroup import UserGroup
from nextres.database.util import Base


class User(Base, UserMixin):
    __tablename__ = 'users'
    kerberos = Column(String(8), primary_key=True)

    discord_id = Column(String(32))
    discord_username = Column(String(32))
    discord_discriminator = Column(Integer)

    groups = relationship('Group', UserGroup)
    guests = relationship('Guest', backref='host', lazy='dynamic', cascade='save-update, merge, delete, delete-orphan')
