#!/usr/bin/env python
"""
.. py:currentmodule:: pyMcGill.experimental.phaseMap.Phase
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
import numpy as np
import scipy.ndimage as ndimage

# Local modules.

# Project modules

# Globals and constants variables.

class Phase(object):
    def __init__(self, name, thresholds, elementData):
        self.name = name
        self._thresholds = thresholds
        self._elementData = elementData

    def getData(self, color, dilationErosion=False):
        width, height = list(self._elementData.values())[0].shape
        rgb_R = np.zeros((width, height), dtype=np.float32)
        rgb_G = np.zeros((width, height), dtype=np.float32)
        rgb_B = np.zeros((width, height), dtype=np.float32)

        compound_index = np.ones((width, height), dtype='bool')

        for element in self._thresholds:
            dataElement = self._elementData[element]
            thresholdMin, thresholdMax = self._thresholds[element]
            compound_index &= dataElement >= thresholdMin
            compound_index &= dataElement <= thresholdMax

        if dilationErosion:
            struct = ndimage.generate_binary_structure(2, 2)

            compound_index = ndimage.binary_closing(compound_index, struct, iterations=1)
            compound_index = ndimage.binary_opening(compound_index, struct, iterations=1)
            compound_index = ndimage.binary_closing(compound_index, struct, iterations=2)
            compound_index = ndimage.binary_opening(compound_index, struct, iterations=2)
            compound_index = ndimage.binary_closing(compound_index, struct, iterations=1)

        rgb_R[compound_index] = color[0]
        rgb_G[compound_index] = color[1]
        rgb_B[compound_index] = color[2]
        data = np.dstack((rgb_R, rgb_G, rgb_B))

        return data

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name

if __name__ == '__main__': #pragma: no cover
    import pyHendrixDemersTools.Runner as Runner
    Runner.Runner().run(runFunction=None)
