## [1.3.2] - 2017-03-06

### Fixed
* Add a longer worker timeout for sending. Seems default 180 seconds is not enough in cases where post will be delivered to a lot of hosts. Allow setting a long timeout, defaulting to 1080 seconds.
* Refactor sending to not send payload multiple times in the case that multiple entities are found in the payload. In reality this should never happen, since Diaspora payloads have one top level entity only.

## [1.3.1] - 2017-01-28

### Fixed
* Diaspora changed their timestamp format in release 0.6.3. This release brings federation support for this timestamp format. Any relay that wants to relay content from Diaspora upgraded Diaspora nodes must upgrade to this release asap.

### Added
* Tests are now built also against Python 3.6.

## [1.3.0] - 2017-01-11

### Backwards incompatible changes

#### Database engines

**Important!** Removed support for SQLite. Added support for PostgreSQL and MySQL/MariaDB.

Reason for this is that SQLite simply will not scale for more than one worker running. With increased adoption of the relay system within The Federation, relays will have to deal with more traffic in the future. Thus, a proper database is needed.

Relays upgrading should not worry too much about migrating the old data over. That can be done but due to limited amount of nodes sending participations at this moment, routing doesn't yet use the database that much. There are no schema changes in this upgrade so if you wish to move the data from the SQLite DB, it should be relatively easy to do so.

#### RQ worker wrapper

The old wrapper `runworker.py` has been removed. This was initially added to easily provide a way to run a worker using the already existing Redis configuration. It's better however to use the cli command provided by RQ to not have to maintain our own wrapper, and to be able to use all the available cli options.

To run a worker, use the following command:

    rqworker -c social_relay.config receive
    
Note! See `circus` note below for recommended way of running workers in production.

### Added
- Added `circus` to handle running jobs and and one or more workers comfortably via one command. This removes the need to separately ensure jobs and workers are running. To use `circus`, either install it via `requirements/production.txt` or separately with `pip install circus`. To run jobs and workers, use the following command: `RQWORKER_NUM=5 circusd extras/circus/circus.ini` - specifying in the variable the amount of workers you want running.

## [1.2.0] - 2016-10-25

### Added
- Expose [NodeInfo](https://github.com/jhass/nodeinfo) to allow registering relays to pod lists. Unfortunately, NodeInfo schema doesn't contain the relay software key so this NodeInfo document cannot be validated by consumers.
- Network calls now use a custom user agent `Social-Relay/<version> - https://github.com/jaywink/social-relay`. Thanks @bmanojlovic for the patch.
- Relay also Diaspora `retraction` and `photo` entities. The former follows the same way `like` and `comment` entities are relayed, ie the targets are the same as where the `status_message` or `photo` were relayed. `photo` follows same rules as `status_message` entities, ie according to subscriber wishes.

### Changed
- Replaced custom payload sending with the new helper from `federation`. This will not try to deliver to `http` targets at all. This means nodes that are not using https will not get deliveries. Really, these days, there is no reason to run a public website with http.

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
