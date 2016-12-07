#!/usr/bin/env python
"""
.. py:currentmodule:: pyxrayphasemap.gui.preferences
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Preferences module for x-ray phase map application GUI.
"""

###############################################################################
# Copyright 2016 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

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
