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

from nextres.database.models.usergroup import UserGroup
from nextres.database.util import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    kerberos = db.Column(db.String(8), primary_key=True)

    discord_id = db.Column(db.String(32))
    discord_username = db.Column(db.String(32))
    discord_discriminator = db.Column(db.Integer)

    groups = db.relationship('Group', UserGroup)
    guests = db.relationship('Guest', backref='host', lazy='dynamic', cascade='save-update, merge, delete, delete-orphan')
