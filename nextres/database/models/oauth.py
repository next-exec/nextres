from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from nextres.database.models.user import User
from nextres.database.util import db


class OAuth(db.Model, OAuthConsumerMixin):
    kerberos = db.Column(db.String(8), db.ForeignKey(User.kerberos))
    user = db.relationship(User)
