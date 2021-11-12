from flask import flash, render_template, request
from flask_login import current_user, login_required

from nextres.constants import FLASH_ERROR, FLASH_SUCCESS
from nextres.controllers.auth import AuthController
from nextres.database import db
from nextres.database.models.guest import Guest, GuestListType

class GuestListController:
    def __init__(self, app):
        @app.route('/guestlist', methods=['GET', 'POST'])
        @login_required
        @AuthController.instance.authorize.in_group('residents')
        def guestlist():
            entries = []
            if request.method == 'POST':
                form = request.form
                kerberoi = form.getlist('kerberoi')
                # jank. jank. jank. jank. jank.
                entries = list(map(list, zip(kerberoi, form.getlist('names'), [''] * 5)))
                if len(entries) != 5:
                    flash('The server received an invalid request. Please contact <a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                          FLASH_ERROR)
                else:
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
                        guests.append(Guest(kerberos=kerberos, name=name, list_type=GuestListType.Desk))
                    if any(map(lambda entry: entry[2], entries)):
                        flash('An invalid guestlist was received. See below.', FLASH_ERROR)
                    else:
                        current_user.guests = guests
                        db.session.commit()
                        flash('Guest list updated successfully!', FLASH_SUCCESS)
            return render_template('guestlist.html',
                                   existing=entries,
                                   desk=current_user.guests.filter_by(list_type=GuestListType.Desk).all(),
                                   express=current_user.guests.filter_by(list_type=GuestListType.Express).all())
