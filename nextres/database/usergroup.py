from nextres.database.util import db

UserGroup = db.Table('user_group', db.Model.metadata,
                     db.Column('kerberos', db.String(8), db.ForeignKey('users.kerberos')),
                     db.Column('group', db.String(255), db.ForeignKey('groups.name')))
