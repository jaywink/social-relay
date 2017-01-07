import os
"""
Testing overrides to config.
"""

ALWAYS_FORWARD_TO_HOSTS = ["sub.example.com"]

if os.environ.get("CI"):
    if os.environ.get("RELAY_DATABASE_TYPE") == "postgresql":
        DATABASE_USER = "postgres"
        DATABASE_PASSWORD = ""
    elif os.environ.get("RELAY_DATABASE_TYPE") == "mysql":
        DATABASE_USER = "root"
        DATABASE_PASSWORD = ""
else:
    DATABASE_USER = "socialrelaytest"
    DATABASE_PASSWORD = "socialrelaytest"
DATABASE_NAME = "socialrelaytest"

RELAY_ACCOUNT = "relay@relay.local"
RELAY_GUID = "jvfhieuhfuih78fhf8uibhfhuyweyfdu"
SECRET_KEY = 'fehufihewiuhfwe78fwe7y8fuiweifuwehjfbuwyehfbuywehfuiwe'
