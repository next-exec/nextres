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

__all__ = ['FormMethodMiddleware', 'PeopleAPI', 'ResponseContext', 'set_group', 'StudentNotFoundException', 'UserConverter', 'WrappedFormRequest']

from flask import render_template, Request
from requests import get
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import BadRequest
from werkzeug.formparser import parse_form_data
from werkzeug.routing import BaseConverter

from nextres.constants import HIERARCHY
from nextres.database import db
from nextres.database.models import Group, User

# https://blog.carsonevans.ca/2020/07/06/request-method-spoofing-in-flask/
# jank nonsense, but it works
class FormMethodMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'].upper() == 'POST':
            _, form, files = parse_form_data(environ)
            environ['wsgi._post_files'] = files
            environ['wsgi._post_form'] = form

            # scripts's python version is also too old for the walrus operator
            method = form.get('_method')
            if method is None:
                pass
            elif method.upper() in ['PATCH', 'PUT', 'DELETE']:
                environ['REQUEST_METHOD'] = method.upper()
            else:
                raise BadRequest()

        return self.app(environ, start_response)

class WrappedFormRequest(Request):
    @property
    def files(self):
        if 'wsgi._post_files' in self.environ:
            return self.environ['wsgi._post_files']
        return super().files

    @property
    def form(self):
        if 'wsgi._post_form' in self.environ:
            return self.environ['wsgi._post_form']
        return super().form

class PeopleAPI:
    instance = None

    def __init__(self, app):
        PeopleAPI.instance = self
        self.authorization = {
            'client_id': app.config['PEOPLE_API_CLIENT_ID'],
            'client_secret': app.config['PEOPLE_API_CLIENT_SECRET']
        }

    def get_kerberos(self, kerberos):
        r = get('https://mit-people-v3.cloudhub.io/people/v3/people/{}'.format(kerberos), headers=self.authorization)
        if r.status_code != 200:
            raise StudentNotFoundException("could not find student '{}'".format(kerberos))
        return Student(r.json())

class Student:
    def __init__(self, data):
        item = data['item']
        self.kerberos = item['kerberosId']
        self.undergrad = item['affiliations'][0]['type'] == 'student'

class StudentNotFoundException(Exception):
    pass

class ResponseContext:
    def __init__(self, template, ctx):
        self.template = template
        self.ctx = ctx

    def __setitem__(self, key, value):
        self.ctx[key] = value

    def return_response(self):
        return render_template(self.template, **self.ctx)

class UserConverter(BaseConverter):
    def to_python(self, kerberos):
        user = db.session.query(User).get(kerberos)
        if user:
            return user
        raise NoResultFound("could not find user '{}'".format(kerberos))

    def to_url(self, user):
        return user.kerberos

def set_group(session, user, group):
    if group == 'none':
        user.groups = []
    else:
        # imagine having get() actually throw an error
        user.groups = [session.query(Group).filter_by(name=name).one() for name in HIERARCHY[HIERARCHY.index(group):]]
    session.commit()
