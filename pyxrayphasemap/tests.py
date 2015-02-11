#!/usr/bin/env python
"""
.. py:currentmodule:: tests
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Regression testing for the project.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Jan 19, 2015"
__copyright__ = "Copyright (c) 2015 Hendrix Demers"
__license__ = "GPL 3"

# Standard library modules.

# Third party modules.

# Local modules.

# Project modules

# Globals and constants variables.

if __name__ == "__main__": #pragma: no cover
    import nose
    import sys
    argv = sys.argv
    argv.append("--cover-package=pyxrayphasemap")
    nose.main(argv=argv)
