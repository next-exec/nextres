# nextres

> next-nextres, the next-next house resident dashboard system

nextres is the latest version of the next house resident dashboard system, intended to replace the older version of nextres written in nodejs.
this project is still a work in progress:

**high priority**

- [x] discord integration
- [x] guest list management
- [ ] room reservations
- [ ] item checkout
- [ ] role management

**enhancements**

- [ ] election voting
- [ ] package management

> **contents**
>
> - [usage](#usage)
> - [installation](#installation)
> - [license](#license)
>   - [agpl-3.0-only](#agpl-30-only)
>   - [mit](#mit)

## usage

once installed, you'll need to make a copy of `config.example.py` in `nextres/` named `config.py` and set up the configuration:

| name | description |
| --- | --- |
| BASE_URL | base url of the nextres installation |
| CGI_ROOT | base path of the nextres installation |
| DISCORD_BOT_TOKEN | token of the discord bot used for the discord account verification feature |
| DISCORD_CLIENT_ID | client id of the discord application used for the discord account verification feature |
| DISCORD_CLIENT_SECRET | client secret of the discord application used for the discord account verification feature |
| DISCORD_VERIFICATION_GUILD | id of the discord guild to place a user in as part of the discord account verification feature |
| DISCORD_VERIFICATION_ROLE | id of the discord role to give a user as part of the discord account verification feature |
| PEOPLE_API_CLIENT_ID | client id for mit people api access used for guest list validation |
| PEOPLE_API_CLIENT_SECRET | client secret for mit people api access used for guest list validation |
| SECRET_KEY | random string used for secure operations |
| SQLALCHEMY_DATABASE_URI | sqlalchemy compatible uri specifying the database for the nextres installation |

in production, nextres will be automatically accessible on the http server it's running on.

in development, nextres can be launched using `pipenv run serve`.
additional debugging capabilities are available via environment variables:

| name | description |
| --- | --- |
| SSL_CLIENT_S_DN_Email | mit email address to authenticate as. this will allow you to access the development server as that user. |

## installation

this project is intended to be installed on [sipb](https://sipb.mit.edu/)'s [scripts](https://scripts.mit.edu/) service.

to install, you'll need the following dependencies:

- [git](https://git-scm.com/) - for cloning the repository
- [nodejs](https://nodejs.org/) - for building frontend dependencies
  - [yarn](https://yarnpkg.com/) - for fetching frontend dependencies
- [python](https://www.python.org/) - for running the server
  - [pipenv](https://pipenv.pypa.io/en/latest/) - for fetching backend dependencies

simply clone the repository to the location you want to install nextres at, fetch the frontend dependencies, build them, and fetch the backend dependencies:

```bash
cd /mit/next/web_scripts/
git clone https://github.com/next-exec/nextres.git
cd nextres/web/
yarn
yarn run production
cd ../
pipenv install
```

## license

this project is licensed under the gnu affero general public license version 3. the contents of `web/src/img/` were originally under the mit license located in LICENSES-img.

### agpl-3.0-only

spdx-license-identifier: agpl-3.0-only

Copyright (C) 2021 Next Exec

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see \<<https://www.gnu.org/licenses/>>

### mit

spdx-license-identifier: mit

Copyright (c) 2013 poofytoo
