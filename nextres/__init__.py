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

from flask import Flask, render_template
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect

from nextres.controllers import *
from nextres.database import FlaskDatabase
from nextres.util import FormMethodMiddleware, PeopleAPI, UserConverter, WrappedFormRequest

app = Flask(__name__)
app.request_class = WrappedFormRequest
app.wsgi_app = FormMethodMiddleware(app.wsgi_app)
app.config.from_pyfile('config.py')
# we don't actually use AUTHORIZE_IGNORE_PROPERTY, but flask-authorize is dumb and crashes without it
app.config.update(AUTHORIZE_IGNORE_PROPERTY='', SQLALCHEMY_TRACK_MODIFICATIONS=True)

# external apis
people = PeopleAPI(app)

# csrf protection
csrf = CSRFProtect(app)

# Initialize database.
database = FlaskDatabase(app)

# model converters
app.url_map.converters['User'] = UserConverter

# Initialize controllers.
auth = AuthController(app)
discord = DiscordController(app)
guestlist = GuestListController(app)
user = UserController(app)


@app.route('/')
@login_required
@auth.group_required('residents')
def index():
    return render_template('index.html')
