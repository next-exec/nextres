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

__all__ = ['OAuth']

from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from nextres.database.models.user import User
from nextres.database.util import Base


class OAuth(Base, OAuthConsumerMixin):
    kerberos = Column(String(8), ForeignKey(User.kerberos, ondelete='cascade', onupdate='cascade'))
    user = relationship(User)
