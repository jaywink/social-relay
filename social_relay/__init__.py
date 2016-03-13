# -*- coding: utf-8 -*-
from flask import Flask
from playhouse.flask_utils import FlaskDB

from social_relay import config

app = Flask(__name__)
app.config.from_object(config)

database = FlaskDB(app)

import social_relay.views

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
