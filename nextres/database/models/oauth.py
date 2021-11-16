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

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from nextres.database.models.user import User
from nextres.database.util import db


class OAuth(db.Model, OAuthConsumerMixin):
    kerberos = db.Column(db.String(8), db.ForeignKey(User.kerberos))
    user = db.relationship(User)
