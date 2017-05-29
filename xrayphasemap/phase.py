#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: xrayphasemap.phase
   :synopsis: Phase to be used in a phase map.
   
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Phase to be used in a phase map.
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
