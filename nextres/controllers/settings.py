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

__all__ = ['SettingsController']

from flask import render_template, request
from flask_login import login_required

from nextres.controllers.auth import AuthController
from nextres.database import db
from nextres.database.models import Settings
from nextres.database.models.settings import SettingsIntegrity

class SettingsController:
    def __init__(self, app):
        group_required = AuthController.instance.group_required

        @app.route('/settings', methods=['GET'])
        @login_required
        @group_required('next_exec')
        def settings_index():
            return render_template('settings/index.html', settings=db.session.query(Settings).first())

        @app.route('/settings', methods=['PUT'])
        @login_required
        @group_required('next_exec')
        def settings_update():
            form = request.form
            express_guest_editable = 'express_guest_editable' in form
            updated_settings = Settings(integrity=SettingsIntegrity.Unique, express_guest_editable=express_guest_editable)
            db.session.merge(updated_settings)
            db.session.commit()
            return render_template('settings/index.html', settings=updated_settings)