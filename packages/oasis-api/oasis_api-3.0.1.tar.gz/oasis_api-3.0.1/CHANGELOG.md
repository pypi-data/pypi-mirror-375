# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- 

### Changed
- 

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- 

## [3.0.1] - 2025-09-09
### Fixed
- Added missing import

## [3.0.0] - 2025-09-09
### Added
- `save_data_h5()` no longer overwrites existing files by default.  
  Attempting to save to an existing filename will now raise a `FileExistsError` unless the user explicitly sets `overwrite=True`.  
  This prevents accidental data loss when saving measurement results.

### Changed
- Version number aligned with firmware v3.x to indicate compatibility.

## [1.0.0] - Skipped
### Changed
- Version number intentionally skipped to align API versioning with firmware v3.x.  
  The next release after `0.9.0-a3` is `3.0.0`.

## [0.9.0-a3] - 2025-08-08
### Added
- Initial public pre-1.0 release (baseline).

[Unreleased]: https://gitlab.com/oasis-acquisition/oasis-api/-/compare/v3.0.1...main
[3.0.1]:      https://gitlab.com/oasis-acquisition/oasis-api/-/compare/v3.0.0...v3.0.1
[3.0.0]:      https://gitlab.com/oasis-acquisition/oasis-api/-/tags/v3.0.0
[0.9.0-a3]:   https://gitlab.com/oasis-acquisition/oasis-api/-/tags/v0.9.0-a3
