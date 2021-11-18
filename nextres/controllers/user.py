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

__all__ = ['UserController']

from flask import flash, render_template, request
from flask_login import login_required

from nextres.constants import FLASH_ERROR, FLASH_SUCCESS, HIERARCHY
from nextres.controllers.auth import AuthController
from nextres.database import db, first_or_instance
from nextres.database.models import User
from nextres.util import PeopleAPI, ResponseContext, set_group, StudentNotFoundException

from email.mime.text import MIMEText
from subprocess import PIPE, Popen

email = """
<html>
  <body>
    <p>Hi there,</p>
    <p>
      You've been granted access to NextRes, Next House's Resident Dashboard system.
      In order to access NextRes, you'll need certificates properly installed on your computer.
      If you don't already have functional certificates, you can find setup instructions on <a href="https://ist.mit.edu/certificates">IS&T's website</a>.
    </p>
    <p>
      Once you're all set up, click <a href="https://nextres.mit.edu/">here</a> to access NextRes.
      NextRes can be used to do a number of things, including:
    </p>
    <ul>
      <li>managing your guest list</li>
      <li>gaining access to the Next House Discord server</li>
    </ul>
    <p>
      Finally, as NextRes is currently a work in progress, please report bugs on
      <a href="https://github.com/next-exec/nextres">GitHub</a> and contact
      <a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> if you have any issues.
    </p>
    <p>- Next Exec</p>
  </body>
</html>
"""

class UserController:
    def __init__(self, app):
        authorize = AuthController.instance.authorize

        @app.route('/users', methods=['GET'])
        @login_required
        @authorize.in_group('desk_captains')
        def user_index():
            return render_template('users/index.html', users=db.session.query(User))

        @app.route('/users', methods=['PUT'])
        @login_required
        @authorize.in_group('next_exec')
        def user_update():
            ctx = ResponseContext('users/index.html', {
                'users': db.session.query(User)
            })
            residents = request.form.get('residents')
            if not residents:
                flash('An invalid list of residents was provided. You must provide a list of kerberoi, with one on each line.', FLASH_ERROR)
                return ctx.return_response()
            kerberoi = residents.split('\r\n')
            invalid = []
            new = []
            for kerberos in kerberoi:
                try:
                    student = PeopleAPI.instance.get_kerberos(kerberos)
                    if not student.undergrad:
                        invalid.append(kerberos)
                except StudentNotFoundException:
                    invalid.append(kerberos)
                user = first_or_instance(db.session, User, kerberos=kerberos)
                if not user.groups:
                    email.append(kerberos)
                    set_group(db.session, user, 'residents')
            # send emails now so that even if there were errors, people don't miss emails as a result
            if new:
                msg = MIMEText(email, 'html')
                msg['Subject'] = 'NextRes Access Granted'
                msg['From'] = 'nextres@mit.edu'
                msg['To'] = 'nextres@mit.edu'
                msg['Cc'] = 'next-techchair@mit.edu'
                msg['Bcc'] = ','.join(map(lambda kerberos: kerberos + '@mit.edu', new))
                p = Popen(['/usr/sbin/sendmail', '-t'], stdin=PIPE)
                p.communicate(msg.as_bytes())
            if invalid:
                flash('The following kerberoi could not be matched to current MIT students: {}'.format(', '.join(invalid)), FLASH_ERROR)
                return ctx.return_response()
            db.session.query(User).filter(~User.kerberos.in_(kerberoi)).delete()
            db.session.commit()
            ctx['users'] = db.session.query(User)
            flash('The new list of residents has been imported successfully!', FLASH_SUCCESS)
            return ctx.return_response()

        @app.route('/users/<User:user>', methods=['PATCH'])
        @login_required
        @authorize.in_group('desk_captains')
        def user_patch(user):
            ctx = ResponseContext('users/index.html', {
                'users': db.session.query(User)
            })
            is_exec = authorize.in_group('next_exec')
            groups = list(map(lambda group: group.name, user.groups))
            if not is_exec and (not user.groups or 'next_exec' in groups):
                flash("You don't have permission to update the group for '{}'.".format(user.kerberos), FLASH_ERROR)
                return ctx.return_response()
            group = request.form.get('group')
            if group not in HIERARCHY + ['none']:
                flash("'{}' is not a valid group.".format(group), FLASH_ERROR)
                return ctx.return_response()
            if not is_exec and group in ['none', 'next_exec']:
                flash("You don't have permission to assign '{}' as a nonresident/Next Exec member.".format(user.kerberos), FLASH_ERROR)
                return ctx.return_response()
            set_group(db.session, user, group)
            # reload users to get updated data
            ctx['users'] = db.session.query(User)
            flash("'{}' assigned successfully!".format(user.kerberos), FLASH_SUCCESS)
            return ctx.return_response()
