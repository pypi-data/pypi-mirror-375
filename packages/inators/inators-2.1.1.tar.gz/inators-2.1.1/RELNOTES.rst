=======================
*inators* Release Notes
=======================

.. start included documentation

2.1.1
=====

Summary of changes:

* Improved the rendering of command-line argument utility documentation by the
  Sphinx extension in ``inators.sphinx``.
* Moved project from flat layout to src layout.
* Improved testing (on Python 3.10, 3.11, 3.12, 3.13, and on PyPy 3.11; also
  linting tests).
* Improved package metadata.
* Improved documentation (also switched to furo theme).
* Dropped support for Python 3.5, 3.6, 3.7, and 3.8.


2.1.0
=====

Summary of changes:

* New module ``inators.sphinx`` to document command-line argument utility code
  (e.g., ``inators.arg``).
* Dropped runtime dependency on setuptools.
* Improved documentation.


2.0.0
=====

Summary of changes:

* Dropped support for Python 2.
* Changed API, introduced keyword-only arguments.
* Improved documentation.
* Improved testing (on PyPy).


1.0.0
=====

First public release of *inators*.

Summary of main features:

* Module ``inators.arg`` to ensure uniform command-line arguments across tools.
* Module ``inators.imp`` to import objects with fully-qualified dotted names.
* Module ``inators.log`` to extend ``logging`` with additional levels.
