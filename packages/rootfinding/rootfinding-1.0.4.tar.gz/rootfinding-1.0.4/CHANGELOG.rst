Changelog
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

1.0.4 (2025-09-08)
------------------

- Deprecate the project.

1.0.3 (2020-09-14)
------------------

- Fix use of wrong types in initialization of module exceptions.

1.0.2 (2020-06-16)
------------------

- Fix `growth_factor` bug in `bracket_root()`.

- Improve documentation of `bracket_root()`.

- `bracket_root()` now raises `ValueError` on an invalid `growth_factor`.

1.0.1 (2020-06-15)
------------------

- `bracket_root()` now raises `ValueError` if passed a negative value as `ftol`.

- Improve descriptions of interval inputs in the API reference.

1.0.0 (2020-06-14)
------------------

First standalone version.
