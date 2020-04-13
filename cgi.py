#!/usr/bin/python3
from nextres import app
from nextres.config import CGI_ROOT

from os import environ
from wsgiref.handlers import CGIHandler

environ['SCRIPT_NAME'] = CGI_ROOT
CGIHandler().run(app)
