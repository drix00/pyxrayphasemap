#!/usr/bin/env python
"""
.. py:currentmodule:: pyxrayphasemap.phase
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Phase to be used in a phase map.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2014 Hendrix Demers"
__license__ = ""

# Standard library modules.

# Third party modules.

# Local modules.

# Project modules

# Globals and constants variables.

class Phase(object):
    def __init__(self, name):
        self.name = name

        self.conditions = {}

    def add_condition(self, data_type, label, minimum=0.0, maximum=None):
        key = (data_type, label)
        self.conditions[key] = (minimum, maximum)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
