# Changelog

All notable changes to this project are documented here.
This file adheres to Keep a Changelog and Semantic Versioning.

## [Unreleased]

## [0.3.1] - 2025-09-09

- Added: Table printing of all OS values.

## [0.3.0] - 2025-09-09

- Added: Support merging in new data to combine observations.
- Added: Tests covering merge behavior.

## [0.2.0] - 2025-09-09

- Added: Additional `os_key` data for broader OS coverage.
- Changed: Improve Linux and macOS parsing; update BSD product extraction; better Windows version identification; fix Darwin kernel parsing.
- Changed: Break up network parsing into vendor-specific modules; general code cleanup; repo structure tidy-up.
- Changed: Rename `OSParse` to `OSData`; project renamed to `os_normalizer`.
- Changed: Adopt Ruff and reformat codebase; fix linter errors; improve test harness.
- Fixed: Failing tests (including `tests/test_full.py`).
- Removed: Old `Observation` class; now parse text and data directly.

## [0.1.0] - 2025-09-06

- Initial release.

[Unreleased]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/johnscillieri/os-normalizer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/johnscillieri/os-normalizer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/johnscillieri/os-normalizer/releases/tag/v0.1.0
