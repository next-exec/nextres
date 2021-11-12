from nextres.database.models.user import User
from nextres.database.util import db

from enum import Enum

class GuestListType(Enum):
    Desk = 1
    Express = 2

class Guest(db.Model):
    __tablename__ = 'guests'
    host_kerberos = db.Column(db.String(8), db.ForeignKey(User.kerberos), primary_key=True)
    kerberos = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    list_type = db.Column(db.Enum(GuestListType), nullable=False)
