#!/usr/bin/env python
"""
.. py:currentmodule:: raw_map
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read raw file map.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Mar 26, 2015"
__copyright__ = "Copyright (c) 2015 Hendrix Demers"
__license__ = "GPL 3"

# Standard library modules.

# Third party modules.
import matplotlib.pyplot as plt

# Local modules.
from pySpectrumFileFormat.Bruker.MapRaw.MapRawFormat import MapRawFormat

# Project modules

# Globals and constants variables.

def run():
    filepath = r"D:\work\results\experiments\SU8230\hdemers\adam\12samples\Adam_12samples_20150316_2015-03-16_17-47\Sample01.raw"
    rawMap = MapRawFormat(filepath)

    plt.figure()

    energy, pixelSpectrum = rawMap.getSpectrum(0, 0)
    plt.plot(energy, pixelSpectrum)

    energy, pixelSpectrum = rawMap.getSpectrum(200, 200)
    plt.plot(energy, pixelSpectrum)

    #plt.figure()

    #image = rawMap.getTotalIntensityImage()
    #plt.imshow(image)

if __name__ == '__main__':  #pragma: no cover
    run()

    plt.show()