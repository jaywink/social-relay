## [unreleased]

### Added
- Expose [NodeInfo](https://github.com/jhass/nodeinfo) to allow registering relays to pod lists. Unfortunately, NodeInfo schema doesn't contain the relay software key so this NodeInfo document cannot be validated by consumers.
- Network calls now use a custom user agent `Social-Relay/<version> - https://github.com/jaywink/social-relay`.

### Removed
- Removed suggestion to use `pip-tools` and convert requirements files to standard Python project requirements files. Didn't dig the workflow after all. To install dev dependencies use `requirements/development.txt`. For production, use `requirements/production.txt`, which also contains `uWSGI`. If you don't deploy using uWSGI, you can just use `requirements/requirements.txt`.

## [1.1.1] - 2016-05-09

### Changed
- Bump `Social-Federation` to 0.3.2. Fixes issue with DiasporaPost processing when actual message content is empty.

## [1.1.0] - 2016-05-08

### Backwards incompatible changes

Python 2.x support has been dropped. The current tested Python versions are 3.5 and 3.6.

### Important!

New dependency, SQLite3 added. Make sure before deploying to install necessary OS packages (`sqlite3` in Ubuntu).

Of course a database means schema migrations. See the readme for instructions on how to create the initial schema and what to do when pulling in a new version of the relay.

### Python dependencies

[pip-tools](https://github.com/nvie/pip-tools) is now used to maintain dependencies. You can still use the normal `pip` commands to install requirements, though using `pip-sync` from pip-tools package will ensure unnecessary packages are also removed. Check the readme.

### Added
- Add SystemD example services (thanks @jpope777).
- Add SQLite database as requirement.
- Started adding test coverage using `py.test`. Tests are run on Travis.
- Add models for storing statistics for received and outgoing payloads. Statistics is shown in the dashboard.
- Add models for posts and nodes. Store post metadata and which nodes were sent to when forwarding to remote nodes. This data is then used to forward participations to the same destinations.
- Add worker and queue statistics to dashboard. Now you can quickly check if no workers are running :)
- Support relaying Diaspora like and comment messages.

### Changed
- Various tweaks and fixes to Ansible role, including upstart configuration for jobs and workers. ALso Ansible now deploys with uWSGI instead of Apache mod_wsgi.
- `runworker.py` wrapper script now uses the app Redis settings (for example DB). This is now the preferred way to run an RQ worker. See readme.
- Bump Social-Federation to latest development version. Note! When deploying, always make sure that Social-Federation updates using the pip `-U` flag.

### Fixes
- Fixed response checking when sending to Diaspora nodes. Previously only 200 status code was understood as success, which meant a retry was made to http, causing double deliveries.
- Fix default POD_LIST_JSON url to be https to save unnecessary redirect.
- Fix webfinger view where 'acct:' is used in the webfinger query

## [1.0.0] - 2015-09-20

Initial release.

- Pulls node lists from a given source.
- Queries nodes for their subscription preferences.
- Receives Diaspora Post type messages.
- Handles minimal identity/discovery related tasks to be a working federation identity.
- Processes receive queue and forwards payloads to subscribers.
