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

from flask import render_template
from flask_login import login_required

from nextres.controllers.auth import AuthController
from nextres.database import db
from nextres.database.models import User

class UserController:
    def __init__(self, app):
        authorize = AuthController.instance.authorize

        @app.route('/users', methods=['GET'])
        @login_required
        @authorize.in_group('desk_captains')
        def user_index():
            return render_template('users/index.html', users=db.session.query(User))
