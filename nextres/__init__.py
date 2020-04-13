from flask import Flask, render_template
from flask_login import login_required

from nextres.controllers import *
from nextres.database import Database

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.update(SQLALCHEMY_TRACK_MODIFICATIONS=True)

# Initialize database.
database = Database(app)

# Initialize controllers.
auth = AuthController(app)


@app.route('/')
@login_required
@auth.authorize.in_group('residents')
def index():
    return render_template('index.html')
