# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [unreleased]
### Added
### Changed
### Fixed
### Removed

## [v0.26.2.0] - 2021-12-12
### Added
- Support extending `fina` CLI in plugins by providing a `plugin.PluginCliOptions` utility class.

## [v0.26.1.0] - 2021-12-05
### Added
- Add `-r`/`--recurrent` option as alias for `-t recurrent` for several commands. (#68)
- dependabot configuration for automated dependency updates.
- Officially support Python 3.10.
### Changed
- Update dependencies `tinydb`, `python-dateutil`, and `argcomplete`.
- Use more modern package structure (`setup.cfg` file, `build` for building wheels). (#67)

## [v0.26.0.0] - 2021-01-22
### Added
- Data and config directories are now sensible for non-UNIX operating systems. XDG environment variables are respected. The dependency `appdirs` is introduced (version 1.4.4) (#65)
### Changed
- Application logs are now stored in an OS-specific cache directory (previously: `~/.local/share/financeager`).
- If the `--frequency` option is used with the `add` command, it is assumed that a recurrent entry shall be added. This avoids accidentally adding a standard entry when missing the `--table-name recurrent` option. (#62)
- In case of an error, `Server.run` returns the Exception object instead of an exception string. This allows for more fine-grained handling in downstream code built on the `server` module. (#49)
### Fixed
- The `name` and `category` fields for `add` or `update` commands are validated at CLI level for being non-empty. This avoids passing invalid data to the backend which would result in a failing validation in the `pockets` module. Trailing whitespace is stripped from `name` and `category` fields.

## [v0.25.0.1] - 2021-01-02
### Fixed
- Specifying a date by format YY-MM-DD for a CLI option is correctly parsed.
- Support four-digit entry IDs (i.e. up to 9999).

## [v0.25.0.0] - 2021-01-01
### Changed
- CI tests are now executed via Github actions instead of Travis.
- The release procedure is executed entirely via Github actions.
- The database structure underwent a major change. It is intended that a single database spans more than a year, and refers to a specific project. Please run the `convert-periods-to-pocket` command to transfer existing data into the new format. The term 'period' is replaced by 'pocket'. Date fields are stored including the year. By default, recurrent entries last infinitely. (#52)
- CLI date parsing is now executed by the `python-dateutil` package instead of only supporting a single format. (#52)
- The dependency `tinydb` is updated to version 4.3.0. (#52)
- The dependency `python-dateutil` is updated to version 2.8.1. (#52)
### Fixed
- Preprocess `--start`/`--end` CLI options for `add` command. (#52)
### Removed
- The `date_format` configuration option is removed. (#52)
- Support for Python 3.5 is removed. The program might become incompatible with that version in an upcoming release.
### Deprecated
- The main command `financeager` is replaced by the shorter and more pleasant `fina`.

## [v0.24.0.0] - 2020-12-05
### Added
- The app is tested against Python 3.9.
### Changed
- The 'none' value for the `SERVICE.name` configuration option is renamed to 'local'.
### Fixed
- Filtering by the 'value' field when using the `list` command now works. (#58)
### Removed
- As announced in v0.23.0.0, flask-webservice related functionality has been moved to a dedicated plugin, [financeager-flask](https://github.com/pylipp/financeager-flask). If you were using the flask-webservice before, install the new package when updating financeager, at least on the client side. (#53)

## [v0.23.1.0] - 2020-03-05
### Added
- Configuration.get_option() returns converted option value if an option was assigned a type (int, float, boolean). Available option types are also used for validating configuration. PluginConfiguration.init_option_types() is added to enable option typing in plugins. (#56)
- The output of the 'list' command shows the difference of total earnings and expenses. (#29)
- The output of the 'list' command shows only category entries incl. their percentage share in total listing values when the '--category-percentage' option is specified. (#33)
- The output of the 'list' command shows only monthly entries with the '--month' option. Default value is the current month. (#55)
- Command line tab completion is provided by the argcomplete package. (#47)
### Changed
- The PluginConfiguration.validate() method is not required to be implemented in derived classes anymore.
- Instead of having Configuration.get_option() return a section if no option was specified, a method get_section() is introduced.
- clients.Client() takes a mandatory keyword argument 'configuration'. (#57)
- 'marshmallow' is used for data validation instead of 'schematics'. (#48)
### Deprecated
- The database structure will undergo a major change in version 0.25.0.0. Please follow the corresponding [issue](https://github.com/pylipp/financeager/issues/52) for more details and about how to migrate.
### Removed
- The Configuration.__getattr__() method enabling 'magic' access of underlying ConfigParser methods.
### Fixed
- The SERVICE:FLASK timeout configuration option is now taken into account if specified in a configuration file.
- Non-error and non-debug program (standard) output is put to stdout instead of stderr. This enables proper redirecting of program output acc. to the norm of a UNIX tool.
- financeager log files are now properly rotated.
- financeager exits with a non-zero exit code if execution errored.
- When invoked without any arguments, financeager now shows usage info instead of a confusing exception traceback.
- Entries added on February 29th can be displayed as result of `list` or `get`.

## [v0.23.0.0] - 2019-12-30
### Added
- Extensibility by plugins. The only group supported so far is 'financeager.services'. Related adjustments in the cli, clients, and config modules. A plugin module is added. (#53)
- New classes FlaskClient and LocalServerClient, as well as factory function create() in clients module.
- Test against Python 3.8 on Travis CI.
### Changed
- Client.Out is renamed to Client.Sinks.
- The versioning scheme now adheres to '0.major.minor.patch' to correctly indicate impacts of new releases. (#54)
- The 'communication' module is renamed to 'clients'.
### Deprecated
- Flask-webservice related functionality will be moved to a dedicated plugin. (#53)
### Removed
- communication.module() and httprequests/localserver.proxy() functions.
### Fixed
- All available Periods are listed with the 'periods' command, even after restarting the webservice, or when using the 'localserver' variant. (#3)

## [v0.22] - 2019-10-30
### Added
- Extend Travis CI (use Python version 3.6 and 3.7, include style checks)
- Add gitlint tool for development.
- Provide version information using setuptools_scm. (#45)

### Changed
- Send any HTTP request data in JSON format.
- Client-side communication interface is abstracted in the Client class.
- Various test framework enhancements.
- [Incompatible] The URL endpoint for copying entries is changed from /periods/copy to /copy. (#32)
- [Incompatible] The `list` command has been renamed to `periods`. (#38)
- [Incompatible] The `print` command has been renamed to `list`. (#38)
- [Incompatible] The `rm` command has been renamed to `remove`. (#40)

### Removed
- `test.suites` module and `test.test_*.suite` functions in order to simplify test framework. Testing now invokes `unittest` discovery in an expected way.
- `test.test_communication` module because it contained redundant tests.

### Fixed
- `list --stacked-layout` displays total values of earnings and expenses (analogous to the output of bare `list`). (#35)
- Database files are properly closed after test runs involving a Flask app. (#42)

## [v0.21] - 2019-08-19
### Added
- Changelog file and related tooling.
