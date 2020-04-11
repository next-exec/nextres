from flask import Flask

from json import load

app = Flask(__name__)

with open('config.json') as fp:
    config = load(fp)
