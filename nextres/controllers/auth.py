from flask import render_template
from flask_authorize import Authorize
from flask_login import LoginManager
from werkzeug.exceptions import Unauthorized

from nextres.database import User
from nextres.database.util import first_or_instance

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
                return first_or_instance(User, kerberos=email.split('@')[0])
