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
from nextres.database import db
from nextres.database.models import User
from nextres.util import ResponseContext, set_group

class UserController:
    def __init__(self, app):
        authorize = AuthController.instance.authorize

        @app.route('/users', methods=['GET'])
        @login_required
        @authorize.in_group('desk_captains')
        def user_index():
            return render_template('users/index.html', users=db.session.query(User))

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
