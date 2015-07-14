# No need to change this normally, override in locals if needed
RELAY_USERNAME = "relay"

# Just something hcard needs, override in locals if you want to customize
# This might appear visible on some pod who fetches the relay hcard...
RELAY_NAME = "Social-Relay"

# Relays only need a public key because Diaspora pods want to read one. So this doesn't need changing normally,
# override in locals if needed
RELAY_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9eofav26VCq3C6g9sIPjiEYzhuiFGGAMx4NAY2bP9NFxXtuERYsqtS+" \
                   "bie101/rjcDEbK5IcZY+jvCGh0P8oI/nj5kSREWxNv3OwRlCbyCtN2XR/eWEs/SfNvZysGtQunLGaUwtcyD+PUXeDuj0PH" \
                   "FuVUEudJ5DiJzu2fcUMGhLv9Xr+C2HU0tcNUjtZmYySsiVXVVrKMzj/Bgefkq7ECy3gchSgYpa2Mc5vOEBG1OxAyQvYDlE" \
                   "IohseDPo5YC9FBjp9gy7caJtvSmM5YQnDP7fjp/ghDSFtVqRWpfJbM2g9R+rAhD6w1JgvBYoOHF0ittOrbPv8WvzhaHivX" \
                   "ZADp relay@localhost"

POD_LIST_JSON = "http://the-federation.info/pods.json"

from social_relay.local_config import *

# Make sure we have a GUID
try:
    assert len(RELAY_GUID) == 32
except Exception:
    print("****\nYOU MUST define 'RELAY_GUID' configuration as 32 chars that will be unique *across* the "
          "whole network.\n****")
    raise

RELAY_ACCOUNT = "%s@%s" % (
    RELAY_USERNAME,
    SERVER_HOST.split("//")[1]
)
