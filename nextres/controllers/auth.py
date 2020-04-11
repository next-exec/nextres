from flask import render_template
from flask_login import LoginManager

from nextres.database import User
from nextres.database.util import first_or_instance

from os import getenv


class AuthController:
    def __init__(self, app):
        self.manager = LoginManager(app)
        self.manager.login_message = None
        self.manager.login_view = 'certificates'

        @app.route('/certificates')
        def certificates():
            return render_template('auth/certificates.html', base=app.config['BASE_URL'])

        @self.manager.request_loader
        def load_kerberos(_):
            email = getenv('SSL_CLIENT_S_DN_Email')
            if email:
                return first_or_instance(User, kerberos=email.split('@')[0])
