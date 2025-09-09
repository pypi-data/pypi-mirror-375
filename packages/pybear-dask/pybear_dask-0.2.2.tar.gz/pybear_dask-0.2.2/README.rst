pybear-dask
===========

|Tests|
|Coverage|
|Test Status 313|
|Test Status 312|
|Test Status 311|
|Test Status 310|

.. |Tests| image:: https://raw.githubusercontent.com/PylarBear/pybear-dask/main/.github/badges/tests-badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions

.. |Coverage| image:: https://raw.githubusercontent.com/PylarBear/pybear-dask/main/.github/badges/coverage-badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions

.. |Test Status 313| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py313.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py313.yml

.. |Test Status 312| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py312.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py312.yml

.. |Test Status 311| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py311.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py311.yml

.. |Test Status 310| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py310.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/matrix-tests-py310.yml

|TestPyPI Build Status|

.. |TestPyPI Build Status| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/testpypi-publish.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/testpypi-publish.yml

|PyPI Build Status|
|Version|
|PyPI Downloads|

.. |PyPI Build Status| image:: https://github.com/PylarBear/pybear-dask/actions/workflows/pypi-publish.yml/badge.svg
   :target: https://github.com/PylarBear/pybear-dask/actions/workflows/pypi-publish.yml

.. |Version| image:: https://img.shields.io/pypi/v/pybear-dask
   :target: https://pypi.org/project/pybear-dask
   :alt: PyPI Version

.. |PyPI Downloads| image:: https://static.pepy.tech/badge/pybear-dask
   :target: https://pepy.tech/project/pybear-dask/
   :alt: PyPI Downloads

|DOI|

.. |DOI| image:: https://zenodo.org/badge/1009051313.svg
   :target: https://doi.org/10.5281/zenodo.16548280
   :alt: DOI

|BMC|

.. |BMC| image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
   :target: https://www.buymeacoffee.com/pybear
   :alt: Buy Me A Coffee

.. |PythonVersion| replace:: >=3.10, <3.13
.. |DaskVersion| replace:: <2025.1.0
.. |DaskMLVersion| replace:: <2025.1.0
.. |DistributedVersion| replace:: <2025.1.0
.. |PybearVersion| replace:: >=0.2.0
.. |PytestVersion| replace:: >=7.0.0



pybear-dask is a Python computing library that supplements the pybear
library with analogous modules that have dask capability.

Website: https://github.com/PylarBear/pybear-dask

License
-------

BSD 3-Clause License. See `License File <https://github.com/PylarBear/pybear-dask/blob/main/LICENSE>`__.

=======

Installation
------------

Dependencies
~~~~~~~~~~~~

pybear-dask requires:

- Python (|PythonVersion|)
- dask (|DaskVersion|)
- dask-ml (|DaskMLVersion|)
- distributed (|DistributedVersion|)
- pybear (|PybearVersion|)

User installation
~~~~~~~~~~~~~~~~~

Install pybear-dask from the online PyPI package repository using ``pip``::

   (your-env) $ pip install pybear-dask

Conda distributions are expected to be made available sometime after release to
PyPI.

=======

Usage
-----
The folder structure of pybear-dask is nearly identical to scikit-learn. This
is so those that are familiar with the scikit layout and have experience with
writing the associated import statements have an easy transition to pybear-dask.
The pybear-dask subfolders are *base* and *model_selection*.

You can import pybear-dask's packages in the same way you would with scikit.
Here are a few examples of how you could import and use pybear-dask modules:

.. code-block:: console

    from pybear-dask.model_selection import GSTCVDask

    search = GSTCVDask()
    search.fit(X, y)

    from pybear-dask import model_selection as ms

    search = ms.AutoGridSearchCVDask()
    search.fit(X, y)


=======

Major Modules
-------------

AutoGridSearchCVDask
~~~~~~~~~~~~~~~~~~~~
Perform multiple uninterrupted passes of grid search with dask_ml GridSearchCV 
and dask objects utilizing progressively narrower search grids.

- Access via pybear-dask.model_selection.AutoGridSearchCVDask.

GSTCVDask (GridSearchThresholdCV for Dask)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perform conventional grid search on a classifier with concurrent threshold 
search using dask objects in parallel and distributed environments. Finds the 
global optima for the passed parameters and thresholds. Fully compliant with 
the dask_ml/scikit-learn GridSearchCV API.

- Access via pybear-dask.model_selection.GSTCVDask.

AutoGSTCVDask (AutoGridSearchThresholdCV for Dask)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perform multiple uninterrupted passes of grid search with pybear-dask GSTCVDask
utilizing progressively narrower search grids.

- Access via pybear-dask.model_selection.AutoGSTCVDask.

=======

Changelog
---------

See the `changelog <https://github.com/PylarBear/pybear-dask/blob/main/CHANGELOG.md>`__
for a history of notable changes to pybear-dask.

=======

Development
-----------

Important links
~~~~~~~~~~~~~~~

- Official source code repo: https://github.com/PylarBear/pybear-dask
- Download releases: https://pypi.org/project/pybear-dask/
- Issue tracker: https://github.com/PylarBear/pybear-dask/issues

Source code
~~~~~~~~~~~

You can clone the latest source code with the command::

    git clone https://github.com/PylarBear/pybear-dask.git

Contributing
~~~~~~~~~~~~

pybear-dask is not ready for contributions at this time!

Testing
~~~~~~~

pybear-dask 0.2 is tested via GitHub Actions to run on Linux, Windows, and MacOS,
with Python versions 3.10, 3.11, and 3.12. pybear-dask is not tested on earlier
versions, but some features may work.

If you want to test pybear-dask yourself, you will need:

- pytest (|PytestVersion|)

The tests are not available in the PyPI pip installation. You can get
the tests by downloading the tarball from the pybear-dask project page on
`pypi.org <https://pypi.org/project/pybear-dask/>`_ or cloning the pybear-dask
repo from `GitHub <https://github.com/PylarBear/pybear-dask>`_. Once you have
the source files in a local project folder, create a poetry environment for the
project and install the test dependencies. After installation, launch the poetry
environment shell and you can launch the test suite from the root of your
pybear-dask project folder with::

    (your-pybear-dask-env) you@your_computer:/path/to/pybear-dask/project$ pytest tests/

Project History
---------------

This project was spun off the main pybear project just prior to the first
public release of both. pybear-dask was spun off to ensure maximum stability
for the main pybear project, while keeping these modules available.

Help and Support
----------------

Documentation
~~~~~~~~~~~~~

Documentation is not expected to be made available via a website for this
package. Use the documentation for similar packages in the main pybear package.
See the repo for pybear: https://github.com/PylarBear/pybear/

Communication
~~~~~~~~~~~~~

- GitHub Discussions: https://github.com/PylarBear/pybear-dask/discussions
- Website: https://github.com/PylarBear/pybear-dask





