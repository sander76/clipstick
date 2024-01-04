# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [Unreleased]

- /

## [0.4.2] - 2024-01-04

### Fixed

- help output when using None in a `Union`. Thanks @NikolayHD !
    
    This has revealed another issue with help output when using `Union` types.
    https://github.com/sander76/clipstick/issues/47
    Will be fixed in next release.

## [0.4.1] - 2024-01-01

### Fixed

- Word wrapping in console output.

## [0.4.0] - 2023-12-30

### Added

- Collection fields. [docs](https://sander76.github.io/clipstick/usage.html#collections)

### Fixed

- Token refactoring
- Re-arranged documentation
- Simplified code

## [0.3.13] - 2023-12-24

### Fixed

- Proper parsing of optional type with `None` as a default.
- Improved help output.
- Replaced dataclasses with normal classes.
- Refactored parsing code [wip].
- Update readme.


## [0.3.12] - 2023-12-21

### Fixed

- Allow for providing optional arguments in an unordered way.
    
    Previously, the parser assumed all optional arguments to follow after
    the positional arguments. This version allows these to be whereever.

## [0.3.11] - 2023-12-20

### Fixed

- remove unused dependency
- fix multiline help output (remove the indent)

## 0.3.10

- update pypi metadata

## 0.3.9

- move to sphinx for documentation

## 0.3.8

- fix wrong reference help file. (readme update)

## 0.3.7

- minor readme update.

## 0.3.6

- better help and error output.

## 0.3.5

- better help and error output.
- refactor tests.

## 0.3.4

- Ad py.typed

## 0.3.3

- Add coverage

## 0.3.2

- Improve validation error output.

## 0.3.1

- Improve help output.

## 0.3.0

- Add short flags for optionals and boolean flags.

## 0.2.1

- update examples

## 0.2.0

- updated readme.
- updated help output.
