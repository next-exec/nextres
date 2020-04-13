from flask_login import UserMixin

from nextres.database.usergroup import UserGroup
from nextres.database.util import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    kerberos = db.Column(db.String(8), primary_key=True)

    discord_id = db.Column(db.String(32))
    discord_username = db.Column(db.String(32))
    discord_discriminator = db.Column(db.Integer)

    groups = db.relationship('Group', UserGroup)
