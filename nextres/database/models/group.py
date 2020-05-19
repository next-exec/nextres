from flask_authorize import AllowancesMixin

from nextres.database.util import db


class Group(db.Model, AllowancesMixin):
    __tablename__ = 'groups'
    name = db.Column(db.String(255), primary_key=True)
