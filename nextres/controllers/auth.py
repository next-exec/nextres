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
from flask_authorize import Authorize
from flask_login import LoginManager
from werkzeug.exceptions import Unauthorized

from nextres.database import Group, User
from nextres.database.util import db, first_or_instance

from os import getenv


class AuthController:
    instance = None

    def __init__(self, app):
        AuthController.instance = self
        self.manager = LoginManager(app)
        self.manager.login_message = None
        self.manager.login_view = 'certificates'
        self.authorize = Authorize(app)

        @app.errorhandler(Unauthorized)
        def unauthorized(_):
            return render_template('auth/nonresident.html'), 403

        @app.route('/certificates')
        def certificates():
            return render_template('auth/certificates.html', base=app.config['BASE_URL'])

        @self.manager.request_loader
        def load_kerberos(_):
            email = getenv('SSL_CLIENT_S_DN_Email')
            if email:
                return first_or_instance(db.session, User, kerberos=email.split('@')[0])
