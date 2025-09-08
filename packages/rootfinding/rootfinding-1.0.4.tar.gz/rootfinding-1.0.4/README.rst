``rootfinding``: find roots of scalar functions
===============================================

**⚠️ This project is deprecated and no longer maintained**

.. image:: https://img.shields.io/pypi/v/rootfinding.svg
   :target: https://pypi.org/project/rootfinding/
   :alt: PyPI

.. image:: https://github.com/gerlero/rootfinding/workflows/CI/badge.svg
   :target: https://github.com/gerlero/rootfinding/actions
   :alt: GitHub Actions - CI

.. image:: https://img.shields.io/codecov/c/gh/gerlero/rootfinding
  :target: https://codecov.io/gh/gerlero/rootfinding
  :alt: codecov - Code coverage

.. image:: https://img.shields.io/readthedocs/rootfinding.svg
   :target: https://rootfinding.readthedocs.io
   :alt: Read the Docs - Documentation

.. image:: https://img.shields.io/pypi/pyversions/rootfinding.svg
   :target: https://pypi.org/project/rootfinding/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/l/rootfinding.svg
   :target: https://github.com/gerlero/rootfinding/blob/master/LICENSE.txt
   :alt: PyPI - License


``rootfinding`` finds roots by bisecting a bracketing interval until the value of the function can be considered sufficiently close to zero. The scheme differs slightly from the implementation of bisection in SciPy_: it is better suited for cases where a maximum acceptable residual is a more useful termination criterion than a tolerance for the argument variable, and can lead to fewer function evaluations overall.

The small library also contains functionality to automatically search for a bracket of a root when one is not known. While the library will always start by checking the inputs, it is possible to avoid redundant function calls by providing known values of the function—similarly, objects returned (and exceptions raised) by the library helpfully include function values that may be of interest. ``rootfinding`` was first developed as an internal module of our other project Fronts_.

To use this library, install ``rootfinding`` from PyPI_ as ``$ pip install rootfinding``. Alternatively, you may copy the ``rootfinding.py`` file from the source code directly into your project (you must retain the copyright notice and license).

.. _SciPy: https://docs.scipy.org/doc/scipy/reference/optimize.html#scalar-functions
.. _Fronts: https://github.com/gerlero/fronts
.. _PyPI: https://pypi.org/project/rootfinding

.. doc-inclusion-marker

Documentation is available on `Read the Docs`_.

.. _Read the Docs: https://rootfinding.readthedocs.io
