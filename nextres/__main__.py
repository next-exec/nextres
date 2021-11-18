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

from nextres import app
from nextres.database import CLIDatabase
from nextres.database.models import Group, User
from nextres.database.util import first_or_instance

from argparse import ArgumentParser

HIERARCHY=['next_exec', 'desk_captains', 'desk_workers', 'residents']

def assign(args):
    # needed because of flask mixins. we were *this* close to separation of concerns. *sigh*
    with app.app_context():
        with CLIDatabase() as session:
            user = first_or_instance(session, User, kerberos=args.kerberos)
            if args.group == 'none':
                user.groups = []
            else:
                user.groups = [session.query(Group).filter_by(name=group).one() for group in HIERARCHY[HIERARCHY.index(args.group):]]
            session.commit()


if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    assign_parser = subparsers.add_parser(name='assign', description='assign a user to a specific group')
    assign_parser.set_defaults(func=assign)
    assign_parser.add_argument('kerberos')
    assign_parser.add_argument('group', choices=HIERARCHY + ['none'])
    args = parser.parse_args()
    args.func(args)
