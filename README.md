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

Pretty much normal Python + WSGI setup, just install the requirements and serve using WSGI. For Ubuntu 14.04,
an Ansible role is provided. It will run also the scheduled jobs and a worker via upstart.

### License

AGPLv3
