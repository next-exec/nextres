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

__all__ = ['AuthController']

from flask import render_template
from flask_authorize import Authorize
from flask_login import LoginManager
from werkzeug.exceptions import Unauthorized

from nextres.database import Group, User
from nextres.database.util import db, first_or_instance

from functools import wraps
from os import getenv


class AuthController:
    instance = None

    def __init__(self, app):
        AuthController.instance = self
        self.manager = LoginManager(app)
        self.manager.login_message = None
        self.manager.login_view = 'certificates'
        self.authorize = Authorize(app)

        # used to define more specific errors that can be used to return specific unauthorized pages
        def group_authorizer(group):
            def wrapper(func):
                @wraps(func)
                def caller(*args, **kwargs):
                    try:
                        return self.authorize.in_group(group)(func)(*args, **kwargs)
                    except Unauthorized:
                        raise UnauthorizedGroup(group)
                return caller
            return wrapper

        self.group_required = group_authorizer

        @app.errorhandler(UnauthorizedGroup)
        def unauthorized(e):
            return render_template(e.template), 403

        @app.route('/certificates')
        def certificates():
            return render_template('auth/certificates.html', base=app.config['BASE_URL'])

        @self.manager.request_loader
        def load_kerberos(_):
            email = getenv('SSL_CLIENT_S_DN_Email')
            if email:
                return first_or_instance(db.session, User, kerberos=email.split('@')[0])

class UnauthorizedGroup(Unauthorized):
    def __init__(self, group):
        self.template = 'auth/{}.html'.format(group)
