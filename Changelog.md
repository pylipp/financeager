# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased
### Added
### Changed
### Deprecated
### Removed
### Fixed

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
