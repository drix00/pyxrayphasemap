Developper guide
================

Install the package in development mode::

   py -3 -m pip install -e .

See the list of installed packages in development mode::

   py -3 -m pip list -e.

Create a pip wheel file using setup.py::

   py -2 setup.py bdist_wheel -d dist
   py -3 setup.py bdist_wheel -d dist

Create the html documentation go in the ``docs`` folder of the project and run::

   make clean
   make html
