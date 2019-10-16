# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased
### Added
- Extend Travis CI (use Python version 3.6 and 3.7, include style checks)
- Add gitlint tool for development.

### Changed
- Send any HTTP request data in JSON format.
- Client-side communication interface is abstracted in the Client class.
- Various test framework enhancements.
- [Incompatible] The URL endpoint for copying entries is changed from /periods/copy to /copy. (PR#32)
- [Incompatible] The `list` command has been renamed to `periods`. (#38)
- [Incompatible] The `print` command has been renamed to `list`. (#38)

### Deprecated

### Removed
- `test.suites` module and `test.test_*.suite` functions in order to simplify test framework. Testing now invokes `unittest` discovery in an expected way.

### Fixed

## [v0.21] - 2019-08-19
### Added
- Changelog file and related tooling.
