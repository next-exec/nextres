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

__all__ = ['GuestListController']

from flask import flash, render_template, request
from flask_login import current_user, login_required
from requests import get

from nextres.constants import FLASH_ERROR, FLASH_SUCCESS
from nextres.controllers.auth import AuthController
from nextres.database import db
from nextres.database.models import User
from nextres.database.models.guest import Guest, GuestListType
from nextres.util import PeopleAPI, ResponseContext, StudentNotFoundException

from re import fullmatch

class GuestListController:
    def __init__(self, app):
        authorization = {
            'client_id': app.config['PEOPLE_API_CLIENT_ID'],
            'client_secret': app.config['PEOPLE_API_CLIENT_SECRET']
        }

        @app.route('/guestlists', methods=['GET'])
        @login_required
        @AuthController.instance.authorize.in_group('desk_workers')
        def guestlist_index():
            return render_template('guestlists/index.html', residents=db.session.query(User).filter(User.groups.any(name='residents')).all(), list_type=GuestListType.Desk)

        @app.route('/guestlists/me', methods=['GET'])
        @login_required
        @AuthController.instance.authorize.in_group('residents')
        def guestlist_edit():
            return render_template('guestlists/edit.html',
                                   existing=None,
                                   desk=current_user.guests.filter_by(list_type=GuestListType.Desk).all(),
                                   express=current_user.guests.filter_by(list_type=GuestListType.Express).all())

        @app.route('/guestlists/me', methods=['PUT'])
        def guestlist_update():
            ctx = ResponseContext('guestlists/edit.html', {
                'existing': None,
                'desk': current_user.guests.filter_by(list_type=GuestListType.Desk).all(),
                'express': current_user.guests.filter_by(list_type=GuestListType.Express).all()
            })
            form = request.form
            kerberoi = form.getlist('kerberoi')
            # jank. jank. jank. jank. jank.
            entries = list(map(list, zip(kerberoi, form.getlist('names'), [''] * 5)))
            if len(entries) != 5:
                flash('The server received an invalid request. Please contact <a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                      FLASH_ERROR)
                return ctx.return_response()
            ctx['existing'] = entries
            guests = []
            previous = []
            duplicates = [kerberos for kerberos in kerberoi if kerberoi.count(kerberos) > 1]
            for entry in entries:
                kerberos, name, _ = entry
                if guest := current_user.guests.filter_by(list_type=GuestListType.Desk, kerberos=kerberos, name=name).first():
                    guests.append(guest)
                    continue
                if kerberos == '' and name == '':
                    # avoid empty kerberos bug
                    continue
                if kerberos == '' and name != '':
                    entry[2] = "kerberos must not be empty if name isn't"
                    continue
                if kerberos != '' and name == '':
                    entry[2] = "name must not be empty if kerberos isn't"
                    continue
                if kerberos in duplicates:
                    entry[2] = 'kerberos must only be on a guest list once'
                    continue
                if not fullmatch('[a-z0-9]*', kerberos):
                    entry[2] = 'kerberos must only contain lowercase letters and numbers'
                    continue
                try:
                    student = PeopleAPI.instance.get_kerberos(kerberos)
                    if not student.undergrad:
                        entry[2] = 'guest must be an undergrad'
                        continue
                except StudentNotFoundException:
                    entry[2] = 'kerberos must belong to a current student'
                    continue
                guests.append(Guest(kerberos=kerberos, name=name, list_type=GuestListType.Desk))
            if any(map(lambda entry: entry[2], entries)):
                flash('An invalid guestlist was received. See below.', FLASH_ERROR)
                return ctx.return_response()
            current_user.guests = guests
            db.session.commit()
            flash('Guest list updated successfully!', FLASH_SUCCESS)
            return ctx.return_response()
