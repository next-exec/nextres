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

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from nextres.config import SQLALCHEMY_DATABASE_URI
from nextres.database.models import *
from nextres.database.util import db, first_or_instance, metadata


class CLIDatabase:
    def __init__(self):
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        metadata.create_all(engine)
        self.__session = Session(engine)
        create_groups(self.__session)

    def __enter__(self):
        return self.__session

    def __exit__(self, exc_type, value, traceback):
        self.__session.close()


class FlaskDatabase:
    def __init__(self, app):
        db.init_app(app)
        with app.app_context():
            db.create_all()
            create_groups(db.session)


def create_groups(session):
    first_or_instance(session, Group, name='residents')
    first_or_instance(session, Group, name='desk_workers')
    first_or_instance(session, Group, name='desk_captains')
    first_or_instance(session, Group, name='next_exec')
    session.commit()
