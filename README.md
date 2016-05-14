[![Build Status](https://travis-ci.org/jaywink/social-relay.svg?branch=master)](https://travis-ci.org/jaywink/social-relay) [![Stories in Ready](https://badge.waffle.io/jaywink/social-relay.png?label=ready&title=Ready)](https://waffle.io/jaywink/social-relay) [![codecov](https://codecov.io/gh/jaywink/social-relay/branch/master/graph/badge.svg)](https://codecov.io/gh/jaywink/social-relay) [![Requirements Status](https://requires.io/github/jaywink/social-relay/requirements.svg?branch=master)](https://requires.io/github/jaywink/social-relay/requirements/?branch=master) [![Code Health](https://landscape.io/github/jaywink/social-relay/master/landscape.svg?style=flat)](https://landscape.io/github/jaywink/social-relay/master)

# Social-Relay

Application to act as a relay for public posts using the Diaspora protocol. Keeps track of nodes and their subscription preferences, receives payloads and forwards the payloads to subscribers. The aim is to pass public posts around in an efficient way so any new node in the network can quickly subscribe to lots of public activity, without having to wait a long time to create social relationships.

## How does one integrate to the relay system? How do I write my own relay?

See [relay design concept](https://github.com/jaywink/social-relay/blob/master/docs/relays.md).

Original idea for the relay system can be found in the [diaspora* project wiki](https://wiki.diasporafoundation.org/Relay_servers_for_public_posts).

## Requirements

* Python 3.x (tested on 3.4/3.5)
* Redis
* SQLite3
* Packages for building LXML (required by Social-Federation library):
   - libxml2-dev
   - libxslt-dev
   - lib32z1-dev
   - python3-dev
       - Alternatively, install `python-lxml` package, for example, if you don't want to install everything in a virtual env.

Optional (for better dependency management):
* Pip 6.1 or later
* pip-tools

### Python libraries

Pip-tools is a nifty package to pin requirements. You can do `pip install -r requirements/requirements.txt` to install the Python requirements as in any regular project, but `pip-tools` will also ensure removal of unnecessary packages.

First, make sure `pip` is up-to-date and install `pip-tools`. Note, currently pip-tools<1.7 does not support pip>8.1.1.

    pip install -U pip==8.1.1
    pip install pip-tools

Then install the requirements:

    pip-sync requirements/requirements.txt

Run the `pip-sync` command after every refresh of the relay code to install/remove packages.

## Configuring

Create local config:

    cp social_relay/local_config.py.example social_relay/local_config.py

Edit the `local_config.py` file as instructed in the file.

## Database

The SQLite database needs an initial schema creation. Do this with:

    arnold up 0

The same command should always be run when fetching new relay code. It will migrate any new schema changes.

### RQ Dashboard

An RQ dashboard can be found at `/rq`. Enable it in `social_relay/local_config.py` by setting `RQ_DASHBOARD = True`.
You must also set a username and password in the same file.

## Static files

Bower is used to pull in some JavaScript libs. [Install it first](http://bower.io/) if needed. Then run `bower install`.

Statics are server under the `/static` path which should be server by the web server.

## Running tasks

For normal operation, scheduled jobs should always be running. They take care of refreshing the pod list and polling pods for their subscription preferences. Without these scheduled jobs, the relay will not be able to function.

Keep this running:

    python -m tasks.schedule_jobs

## Processing receive queue

Incoming posts are stored in Redis and processed using RQ workers. Keep one or more worker running always.

To make use of the app configuration for Redis in `social_relay/local_config.py`, use the provided `runworker.py` wrapper, as follows:

    python runworker.py receive

If you do run a worker via `rqworker` command directly, make sure to use the same Redis database as set in app configuration.

## Deployment

Pretty much normal Python + WSGI setup, just install the requirements and serve app using WSGI and statics via the web server. See the following sections for platform specific helpers.

An Apache2 site example can be found [here](https://github.com/jaywink/social-relay/blob/master/ansible/roles/social-relay/templates/apache.conf.j2). The same folder also has examples for upstart init jobs.

### Ansible (Ubuntu)

An Ansible role written for Ubuntu is provided in `ansible` directory. The role uses uWSGI and Apache to serve the app. It will run also the scheduled jobs and a worker. Everything is handled by upstart.

Tested with Ubuntu 14.04 LTS.

### SystemD service files

There are example systemd service files in the 'extra' directory. The examples
use a specific user and utilize gunicorn. They have been tested on CentOS 7.

To use, modify as needed (user, group, and path), copy to `/etc/systemd/service`
and start/enable as such:

    systemctl start social-relay_server.service
    systemctl start social-relay_tasks.service
    systemctl start social-relay_rqworker@receive.service
    systemctl start social-relay.target

    systemctl enable social-relay_server.service
    systemctl enable social-relay_tasks.service
    systemctl enable social-relay_rqworker@receive.service
    systemctl enable social-relay.target

The rqworker service file can also be used to start the optional `failed` queue as well.

    systemctl start social-relay_rqworker@failed.service

## Development

### Running a development server

This is not the recommended way for a production server. For testing and development, run the server:

    python devserver.py

### Running tests

Make sure you have installed requirements using the command:

    pip-sync requirements/development.txt

Execute `py.test` to run the tests.

### Updating requirements files

When changing dependencies, make sure to update the requirements files:

    pip-compile --output-file requirements/requirements.txt requirements/requirements.in
    pip-compile --output-file requirements/development.txt requirements/requirements.in requirements/development.in
    pip-compile --output-file requirements/requirements-ansible.txt requirements/requirements.in requirements/requirements-ansible.in

## Author

Jason Robinson / @jaywink / https://jasonrobinson.me / https://iliketoast.net/u/jaywink

## License

AGPLv3
