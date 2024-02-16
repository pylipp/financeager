# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [unreleased]
### Added
### Changed
### Fixed
### Removed
### Deprecated

## [v1.3.6] - 2024-02-16
### Changed
- Update dependencies `argcomplete` and `marshmallow`. (#197, #203)
- Update GitHub actions.

## [v1.3.5] - 2024-01-04
### Changed
- Fix permission for GitHub release action.

## [v1.3.4] - 2024-01-03
### Changed
- Use PyPI trusted publishing when uploading package.

## [v1.3.3] - 2024-01-03
### Changed
- Update dependencies `argcomplete` and `rich`. (#185, #187, #188, #191)

## [v1.3.2] - 2023-10-08
### Added
- Support Python 3.12.
### Changed
- Update dependencies `rich`, `marshmallow`, and `argcomplete`. (#171,#174,#175,#178,#181)

## [v1.3.1] - 2023-07-16
### Changed
- Update dependencies `rich` and `tinydb`. (#169,#170)

## [v1.3.0] - 2023-05-05
### Changed
- Update dependencies `rich` and `argcomplete`. (#161,#163)
### Removed
- Support for Python 3.7 is removed.

## [v1.2.1] - 2023-04-03
### Changed
- Update dependencies `rich` and `tinydb`. (#149,#150,#157)

## [v1.2.0] - 2023-01-03
### Added
- New `--json` option for `list` command to return result in JSON format instead of formatted as table (#120). Helpful for processing data with jq or similar tools (refine selection with `--filter` option):
    - all IDs of standard entries: `fina list --json | jq -r '.standard | keys[]'`
    - all IDs of recurrent entries: `fina list --json | jq -r '.recurrent | keys[]'`
    - all IDs of recurrent entries: `fina list --json --recurrent-only | jq .[].eid`

## [v1.1.6] - 2023-01-02
### Changed
- Update dependencies `rich` and `marshmallow`. (#140,#142)

## [v1.1.5] - 2022-11-07
### Changed
- Update GitHub actions to avoid deprecation warnings during CI runs. (#134)

## [v1.1.4] - 2022-11-06
### Added
- Officially support Python 3.11. (#133)
### Changed
- Update dependency `rich`. (#131)

## [v1.1.3] - 2022-10-11
### Changed
- Make project entirely free from `setup.py` (update local `setuptools` and `pip`). (#127)

## [v1.1.2] - 2022-10-10
### Changed
- Update dependency `marshmallow`. (#124,#126)
- Checks for dependency updates are run monthly instead of weekly.
- Use `pyproject.toml` instead of `setup.cfg` for project configuration. (#127)

## [v1.1.1] - 2022-08-17
### Changed
- Update dependencies `rich` and `marshmallow`. (#114,#117)
- Update wording of debug logging message for clarity.
### Fixed
- Filtering for multiple patterns with `fina list`, when one of the filters is `category`, now returns the correct selection instead of an empty result.

## [v1.1.0] - 2022-06-04
### Removed
- Support for Python 3.6 is removed.
### Changed
- Update dependencies `rich` and `marshmallow`. (#104,#105,#106,#109,#111,#112)

## [v1.0.3] - 2022-04-05
### Changed
- Update dependencies `rich` and `marshmallow`. (#98,#99,#101,#102)
### Deprecated
- Python 3.6 support will be removed in `financeager` v1.1.0.

## [v1.0.2] - 2022-02-24
### Changed
- Update dependencies `rich` and `tinydb`. (#95,#97)

## [v1.0.1] - 2022-02-01
### Added
- Output short message when running `list` command but no data found.
### Changed
- Update dependency `rich`. (#91)
### Fixed
- Avoid excessive empty space in table with `list --category-percentage`.

## [v1.0.0] - 2022-01-28
### Added
- Filtering for recurrent entries with indefinite end is now supported (omit the filter value, as in `list -f end=`). (#80)
- Colorful and formatted output from the `list` command via the `rich` package is available.
### Changed
- For filtering the output of the `list` command, the `-f` option can now be specified multiple times with one argument each (previously, multiple arguments could be passed but when using `-f` multiple times, the last occurrence would overrule the previous ones). The filters are combined. The long option is called `--filter` (singular). (#83)
- If the `list -f` option is used with a filter for frequency, start, or end, the `-r/--recurrent-only` option is automatically added. (#83)
- If the `update` command is used with the option `--start` and/or `--end`, it is assumed to operate on recurrent entries. (#84)
- Update dependencies `argcomplete` and `tinydb`. (#81,#85,#87)
- Clarify command line help.
### Removed
- Remove `convert-periods-to-pocket` command. (#78)

## [v0.27.0.1] - 2022-01-24
### Fixed
- Avoid `Invalid configuration` error if default config file does not exist.

## [v0.27.0.0] - 2022-01-03
### Changed
- Using the `list` command with the `--month` option only returns entries of specified month in current year. (#79)
### Removed
- Remove `financeager` command line entry point (deprecated for one year, see v0.25.0.0) (#76)

## [v0.26.3.4] - 2021-12-30
### Fixed
- Prefix path for release notes in Github action.

## [v0.26.3.1] - 2021-12-30
### Changed
- Update action for publishing Github release.

## [v0.26.3.0] - 2021-12-28
### Added
- Add `--recurrent-only` option for `list` command. Filtering using `-f` and sorting using `--entry-sort` are supported. (#51)
- Support updating `end` field for recurrent entries as unset (i.e. indicating no end).
- Support updating `category` field for entries as unset (i.e. indicating unspecified category).
### Changed
- Use `black` as code formatter.
### Removed
- Remove support for Python 3.5 for good (broken since v0.26.1.0 anyways). (#59)
### Deprecated
- The `convert-periods-to-pocket` command will be removed in version `1.0.0`.

## [v0.26.2.1] - 2021-12-16
### Fixed
- Avoid crash in `cli._parse_command()` when using plugin without `cli_options` attribute.

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
