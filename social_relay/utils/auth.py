from flask import Response, request

from social_relay import app


def check_auth(username, password):
    """This function is called to check if a username password combination is valid."""
    return username == app.config.get("RQ_DASHBOARD_USERNAME") and \
           password == app.config.get("RQ_DASHBOARD_PASSWORD")


def authenticate():
    """Sends a 401 response that enables basic auth."""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def basic_auth():
    """Ensure basic authorization."""
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
