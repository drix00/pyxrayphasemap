How to install on Windows
=========================

This a guide to install on Windows, but it can be applied with minor modification on other platform.

Install Python 3 on windows
---------------------------

* Download python 3 on https://www.python.org/downloads/

   * choose the latest version of 3.X.X (3.4.3) and the 64-bit version (Windows x86-64 MSI installer on https://www.python.org/downloads/release/python-343/)

* Install python 3 by double click on python-3.4.3.amd64.msi

   * in the Customize python dialog, choose "Add python.exe to Path" (last option)
   * finish the installation
   * open a command line window (cmd.exe) by typing cmd in Start->Search programs and files
   * Check if the installation is correct in the cmd::

         >python --version
         Python 3.4.3
         > py -3 --version
         Python 3.4.3

   * If you have more than one version of python installed, you can choose the version using these command::

         > py -2.7
         > py -3

   * See https://docs.python.org/3/using/windows.html#python-launcher-for-windows for more information

* Download all packages needed on http://www.lfd.uci.edu/~gohlke/pythonlibs/

   * Choose the file corresponding to your python version (cp34) and windows (win_amd64 for 64-bit windows)

      * Pillow-2.8.2-cp34-none-win_amd64.whl
      * numpy-1.9.2+mkl-cp34-none-win_amd64.whl
      * matplotlib-1.4.3-cp34-none-win_amd64.whl
      * scipy-0.15.1-cp34-none-win_amd64.whl
      * h5py-2.5.0-cp34-none-win32.whl
      * nose-1.3.7-py3-none-any.whl
      * coverage-3.7.1-cp34-none-win_amd64.whl

* Install whl files with cmd.exe

   * open cmd window
   * change directory to the \*.whl files::

         > cd C:\Users\gauvinWorkstation\Desktop\inbox

   * install one file::

         > py -3 -m pip install -U nose-1.3.7-py3-none-any.whl

   * Repeat installation for all whl files.
   * to install all files do these commands

      * First create a batch file::

         > dir /B *.whl > whlfiles.bat

      * Edit each line to add "py -3 -m pip install -U " before the file name::

         > whlfiles.bat

      If you get an error message, to see which packages were installed correctly use::

         > py -3 -m pip list

      You can try to install numpy and scipy first (in this order) or run the whlfiles.bat again

Install Python package on windows
---------------------------------

 To install any package on windows with PIP do the following command after you have download the pyxrayphasemap-\*.whl

* open cmd window
* change directory to the \*.whl files::

   > cd C:\Users\gauvinWorkstation\Desktop\inbox

* install the packages::

   > py -3 -m pip install -U pySpectrumFileFormat-0.1-py2.py3-none-any.whl
   > py -3 -m pip install -U pyxrayphasemap-0.1.1-py2.py3-none-any.whl

* verify that the package is installed correctly::

   > py -3
   >>> import
   >>> import pyxrayphasemap
   >>>

The installation is correct if you get no error (ImportError)

