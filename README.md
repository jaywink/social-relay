[![Build Status](https://travis-ci.org/jaywink/social-relay.svg?branch=master)](https://travis-ci.org/jaywink/social-relay) [![Stories in Ready](https://badge.waffle.io/jaywink/social-relay.png?label=ready&title=Ready)](https://waffle.io/jaywink/social-relay) [![codecov](https://codecov.io/gh/jaywink/social-relay/branch/master/graph/badge.svg)](https://codecov.io/gh/jaywink/social-relay) [![Requirements Status](https://requires.io/github/jaywink/social-relay/requirements.svg?branch=master)](https://requires.io/github/jaywink/social-relay/requirements/?branch=master) [![Code Health](https://landscape.io/github/jaywink/social-relay/master/landscape.svg?style=flat)](https://landscape.io/github/jaywink/social-relay/master)

# Social-Relay

Application to act as a relay for public posts using the Diaspora protocol. Keeps track of nodes and their subscription preferences, receives payloads and forwards the payloads to subscribers. The aim is to pass public posts around in an efficient way so any new node in the network can quickly subscribe to lots of public activity, without having to wait a long time to create social relationships.

## How does one integrate to the relay system? How do I write my own relay?

See [relay design concept](https://github.com/jaywink/social-relay/blob/master/docs/relays.md).

Original idea for the relay system can be found in the [diaspora* project wiki](https://wiki.diasporafoundation.org/Relay_servers_for_public_posts).

## Installation
       
### System libraries

Depending on your database, you will probably need extra libraries installed.

For databases, PostgreSQL and MySQL/MariaDB are supported, choose one.

#### Python

Python 3.4+ is required.

#### Redis

    # Debian / Ubuntu
    sudo apt-get install redis-server

#### PostgreSQL

    # Debian / Ubuntu
    sudo apt-get install libpq-dev postgresql
    
#### MySQL/MariaDB

    # Debian / Ubuntu
    sudo apt-get install python3-dev libmysqlclient-dev 

    # Red Hat / CentOS
    sudo yum install python3-devel mysql-devel
    
#### Federation

The `federation` dependency `lxml` requires certain libraries present:
 
    # Debian / Ubuntu
    sudo apt-get install libxml2-dev libxslt-dev lib32z1-dev python3-dev

### Python libraries

Create a Python 3.4+ virtualenv and activate it.

Ensure `pip` and `setuptools` are up to date.

    pip install -U pip setuptools

For a production deployment, uWSGI (for app server) and Circus (for running workers) are encouraged. Use the production requirements to install them:

    pip install -r requirements/production.txt
    
Otherwise just use the base requirements and install your favourite WSGI engine manually:

    pip install -r requirements/requirements.txt
    
Additionally, choose your database and install the requirements:

    # PostgreSQL
    pip install -r requirements/postgresql.txt
    
    # MySQL/MariaDB
    pip install -r requirements/mysql.txt

### Configuring

Create local config:

    cp social_relay/local_config.py.example social_relay/local_config.py

Edit the `local_config.py` file as instructed in the file.

### Database

You can set database connection settings as environment variables or in `social_relay/local_config.py` - see `social_relay/config.py` for what to override.

The database needs an initial schema creation. Do this with:

    arnold up 0

The same command should always be run when fetching new relay code. It will migrate any new schema changes.

### RQ Dashboard

An RQ dashboard can be found at `/rq`. Enable it in `social_relay/local_config.py` by setting `RQ_DASHBOARD = True`.
You must also set a username and password in the same file.

### Static files

Bower is used to pull in some JavaScript libs. [Install it first](http://bower.io/) if needed. Then run `bower install`.

Statics are server under the `/static` path which should be server by the web server.

### Running tasks and workers

Scheduled jobs handle the polling of node lists and nodes themselves, to fetch their subscription settings. Without the scheduled jobs the server will not be able to function. RQ workers on the other hand process all the incoming payloads and distribute them onwards to subscribing nodes. At least one RQ worker must be running at all times.

In production, it's easiest to use the provided `circus` configuration. This is installed via the provided production requirements, or `pip install circus` if not using the provided requirements file.

Then, export how many RQ workers you want. If you see your `receive` queue build up, increase this count and restart `circus`.

    export RQWORKER_NUM=5

To start `circus`, virtualenv activated in the project folder:

    circusd extras/circus/circus.ini
    
You can daemonize `circus` by passing an extra `--daemonize` flag.

#### Running tasks manually (without circus)

If you don't want to use `circus`, run the tasks manually.  Keep this running:

    python -m tasks.schedule_jobs

#### Processing receive queue (without circus)

If you don't want to use `circus`, run the workers manually. Run the worker(s) as follows:

    rqworker -c social_relay.config receive

## Deployment

Pretty much normal Python + WSGI setup, just install the requirements and serve app using WSGI and statics via the web server. See the following sections for platform specific helpers.

An Apache2 site example can be found [here](https://github.com/jaywink/social-relay/blob/master/ansible/roles/social-relay/templates/apache.conf.j2). The same folder also has examples for upstart init jobs.

### Ansible (Ubuntu)

An Ansible role written for Ubuntu is provided in `ansible` directory. The role uses PostgreSQL, uWSGI and Apache. It will run also the scheduled jobs and a worker. Everything is handled by upstart.

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

### Additional development requirements

    pip install -r requirements/development.txt

### Running a development server

This is not the recommended way for a production server. For testing and development, run the server:

    python devserver.py
    
The app will be running at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Running an RQ worker

    rqworker -c social_relay.config receive

### Running tests

    py.test

## Author

Jason Robinson / @jaywink / https://jasonrobinson.me

Awesome contributors listed in `CONTRIBUTORS` file.

## License

AGPLv3
