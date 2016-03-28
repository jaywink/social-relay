[![Build Status](https://travis-ci.org/jaywink/social-relay.svg?branch=master)](https://travis-ci.org/jaywink/social-relay) [![Stories in Ready](https://badge.waffle.io/jaywink/social-relay.png?label=ready&title=Ready)](https://waffle.io/jaywink/social-relay)

## Social-Relay

See https://wiki.diasporafoundation.org/Relay_servers_for_public_posts

### Requirements

* Python 3.x (though the frontend works, mostly, with Python 2.x)
* Redis

Python libraries in `requirements/base.txt`.

### Running server

Create local config:

    cp social_relay/local_config.py.example social_relay/local_config.py

Edit the `local_config.py` file as instructed in the file.

Run the server:

    python runserver.py

### RQ Dashboard

An RQ dashboard can be found at `/rq`. Enable it in `social_relay/local_config.py` by setting `RQ_DASHBOARD = True`.
You must also set a username and password in the same file.

### JavaScript

Bower is used to pull in some JavaScript libs. [Install it first](http://bower.io/) if needed. Then run `bower install`.

### Running tasks

To run a single task, do for example:

    python -m tasks.fetch_pod_list

To run all scheduled tasks, keep this running:

    python -m tasks.schedule_jobs

### Processing receive queue

Keep one or more of these running:

    rqworker receive

You might optionally want to run one worker towards the `failed` queue.

Note! If you changed Redis connection parameters in `social_relay/local_config.py`, make sure to pass the right connection parameters when calling `rqworker`. The command line utilities for RQ don't read the configuration for the relay.

### Deploying

Pretty much normal Python + WSGI setup, just install the requirements and serve using WSGI. See the following sections for platform specific helpers.

#### Ansible (Ubuntu)

An Ansible role written for Ubuntu is provided in `ansible` directory. It will run also the scheduled jobs and a worker via upstart.

Tested with Ubuntu 14.04 LTS.

#### SystemD service files

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

### License

AGPLv3
