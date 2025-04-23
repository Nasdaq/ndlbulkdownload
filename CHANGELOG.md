# Changelog

## [v0.2.0] - 2025-04-23

### Added

- Introduce changelog
- Allow users to write files to a desired base path rather than current
  working directory of execution.

### Changed

- Update documentation and help options.
- Lint tooling and development setup.
- Lint changes and code style format improvements guided by tooling (ruff
  format).
- --param switch now accepts multiple values.  Callers can reduce overhead
  when defining multiple argument values and avoid duplication.
- Use HTTP POST body to avoid sending too query parameters for any GET request
  that could exceed server limits.
- Update pytoml metadata to indicate python 3.11 support.

## [v0.1.1] - 2024-12-02

### Added

- Keep track of failed URLs and automatically retry.  Improve resiliency to
  help ensure collection of files are downloaded.  Report failed URLs to
  logging.  Use --verbose to see more; use --debug to see list of failed URLs.

## [v0.1.0] - 2024-09-27

Initial release.

### Added

- Initial feature set allowing users to download Data Link tables for an
  arbitrary set of key-value parameters.  Input depends on table
  specification: users will need to consult the table schema documentation for
  more details.
