activate_this = '/home/socialrelay/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, '/home/socialrelay/socialrelay')
from social_relay import app as application
