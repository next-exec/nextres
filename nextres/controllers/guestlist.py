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

        group_required = AuthController.instance.group_required

        @app.route('/guestlists', methods=['GET'])
        @login_required
        @group_required('desk_workers')
        def guestlist_index():
            return render_template('guestlists/index.html', residents=db.session.query(User).filter(User.groups.any(name='residents')).all(), list_type=GuestListType.Desk)
        
            
        @app.route('/guestlists/me', methods=['PUT','GET'])
        @login_required
        @group_required('residents')
        def guestlist_edit(): 
            if request.method == 'GET':
                  return render_template('guestlists/edit.html',
                                   existing=None,
                                   desk=current_user.guests.filter_by(list_type=GuestListType.Desk).all(),
                                   express=current_user.guests.filter_by(list_type=GuestListType.Express).all())
            else:
                ctx = ResponseContext('guestlists/edit.html', {
                    'existing': None,
                    'existing_express': None,
                    'desk': current_user.guests.filter_by(list_type=GuestListType.Desk).all(),
                    'express': current_user.guests.filter_by(list_type=GuestListType.Express).all()
                })
                form = request.form
                kerberoi = form.getlist('kerberoi')
                express_kerberoi = form.getlist('kerberoi_express')
                all_kerbs = kerberoi + express_kerberoi
                # jank. jank. jank. jank. jank.

                entries = list(map(list, zip(kerberoi, form.getlist('names'), form.getlist('phones'), [''] * 5)))
                express_entries = list(map(list, zip(express_kerberoi, form.getlist('names_express'), form.getlist('mit_id'), [''] * 3)))

                if len(entries) != 5 or len(express_entries) != 3:
                    flash('The server received an invalid request. Please contact <a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                          FLASH_ERROR)
                    return ctx.return_response()
                ctx['existing'] = entries
                ctx['existing_express'] = express_entries
                express_guests = []
                guests = []
                previous = []
                duplicates = [kerberos for kerberos in all_kerbs if all_kerbs.count(kerberos) > 1]
                for express_entry in express_entries:
                    kerberos, name, mit_id, _ = express_entry
                    express_guest = current_user.guests.filter_by(list_type=GuestListType.Express, kerberos=kerberos, name=name, mit_id = mit_id).first()
                    if express_guest:
                        express_guests.append(express_guest)
                        continue
                    if kerberos == '' and name == '' and mit_id =='':
                        # avoid empty kerberos bug
                        continue
                    if kerberos == '':
                        express_entries[3] = "kerberos must not be empty"
                        continue
                    if name == '':
                        express_entries[3] = "name must not be empty if kerberos isn't"
                        continue
                    if mit_id == '':
                        express_entries[3] = "id number must not be empty if kerberos isn't"
                        continue
                    if kerberos in duplicates:
                        express_entries[3] = 'kerberos must only be on a guest list once'
                        continue
                    if not fullmatch('[a-z0-9]*', kerberos):
                        express_entries[3] = 'kerberos must only contain lowercase letters and numbers'
                        continue
                    if len(mit_id) != 9:
                        express_entries[3] = 'id number must contain exactly 9 numbers'
                        continue
                    try:
                        student = PeopleAPI.instance.get_kerberos(kerberos)
                        if not student.undergrad:
                            express_entries[3] = 'guest must be an undergrad'
                            continue
                    except StudentNotFoundException:
                        express_entries[3] = 'kerberos must belong to a current student'
                        continue
                    express_guests.append(Guest(kerberos=kerberos, name=name, mit_id=mit_id, list_type=GuestListType.Express))

                for entry in entries:
                    kerberos, name, phone, _ = entry
                    guest = current_user.guests.filter_by(list_type=GuestListType.Desk, kerberos=kerberos, name=name, phone=phone).first()
                    if guest:
                        guests.append(guest)
                        continue
                    if kerberos == '' and name == '' and phone == '':
                        # avoid empty kerberos bug
                        continue
                    if kerberos == '':
                        entry[3] = "kerberos must not be empty"
                        continue
                    if name == '':
                        entry[3] = "name must not be empty if kerberos isn't"
                        continue
                    if phone == '':
                        entry[3] = "phone must not be empty if kerberos isn't"
                        continue
                    if kerberos in duplicates:
                        entry[3] = 'kerberos must only be on a guest list once'
                        continue
                    if not fullmatch('[a-z0-9]*', kerberos):
                        entry[3] = 'kerberos must only contain lowercase letters and numbers'
                        continue
                    try:
                        student = PeopleAPI.instance.get_kerberos(kerberos)
                        if not student.undergrad:
                            entry[2] = 'guest must be an undergrad'
                            continue
                    except StudentNotFoundException:
                        entry[2] = 'kerberos must belong to a current student'
                        continue
                    guests.append(Guest(kerberos=kerberos, name=name, phone=phone, list_type=GuestListType.Desk))
                if any(map(lambda entry: entry[3], entries)) or any(map(lambda express_entry: express_entry[3], express_entries)):
                    flash('An invalid guestlist was received. See below.', FLASH_ERROR)
                    return ctx.return_response()
                current_user.guests = guests + express_guests
                db.session.commit()
                flash('Guest list updated successfully!', FLASH_SUCCESS)
                return ctx.return_response()
