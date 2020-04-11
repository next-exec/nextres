from flask import Flask

from nextres.database import Database

from json import load

app = Flask(__name__)

with open('config.json') as fp:
    config = load(fp)
app.config.update(SQLALCHEMY_DATABASE_URI=config['database'], SQLALCHEMY_TRACK_MODIFICATIONS=True)

# Initialize database.
database = Database(app)
