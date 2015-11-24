#!/usr/bin/env python
"""
.. py:currentmodule:: pyxrayphasemap.gui.preferences
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Preferences module for x-ray phase map application GUI.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2015 Hendrix Demers"
__license__ = ""

# Standard library modules.

# Third party modules.

# Local modules.

# Project modules

# Globals and constants variables.

class Preferences(object):
    def __init__(self):
        self.verbose = 0

    @property
    def verbose(self):
        return self._verbose
    @verbose.setter
    def verbose(self, verbose):
        self._verbose = verbose
