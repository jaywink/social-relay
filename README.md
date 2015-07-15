## Social-Relay

See https://wiki.diasporafoundation.org/Relay_servers_for_public_posts

### Running server

Create local config:

    cp social_relay/local_config.py.example social_relay/local_config.py
    
Edit the `local_config.py` file as instructed in the file.

Run the server:

    python runserver.py

### Running tasks

To run a single task, do for example:

    python -m tasks.fetch_pod_list
     
To run scheduled tasks, keep this running:
 
    python -m tasks.schedule_jobs

### License

AGPLv3
