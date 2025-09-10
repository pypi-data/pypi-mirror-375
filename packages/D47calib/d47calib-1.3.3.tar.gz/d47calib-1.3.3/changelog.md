# Changelog

## v1.3.3
*Released on 2025-09-10*

### Bugfix
* Fix error introduced by lazy-loading of `typer.rich_utils`.

## v1.3.2
*Released on 2025-03-26*

### Minor new feature
* Add `ignore_samples` option to `combine_D47calibs()`

### Bugfixes
* Fix bug that caused `D47calib.export()` to print out floats as `np.float64()` values with recent versions of numpy
* Fix `SyntaxWarning` related to LaTeX in docstrings

## v1.3.1
*Released on 2023-09-30*

### Minor new feature
* Add `--version` option to CLI

## v1.3
*Released on 2023-09-27*

### Bug fix
* Add `rich` dependency

## v1.2
*Released on 2023-09-19*

### Namespace
* Use `OLGS23` instead of `ogls_2023` as default name for the combined calibration, but keep `ogls_2023` as an alias for now.

## v1.1
*Released on 2023-09-19*

### Bug fix
* Replace `click` with `typer` dependency

## v1.0
*Released on 2023-09-19*

First release