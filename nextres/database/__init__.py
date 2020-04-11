from nextres.database.user import User
from nextres.database.util import db


class Database:
    def __init__(self, app):
        db.init_app(app)
        with app.app_context():
            db.create_all()
