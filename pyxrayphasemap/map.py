#!/usr/bin/env python
"""
.. py:currentmodule:: pyMcGill.experimental.phaseMap.map
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Map used in the phase analysis module.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2014 Hendrix Demers"
__license__ = ""

# Standard library modules.
import logging

# Third party modules.
import numpy as np
from PIL import Image
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import matplotlib

# Local modules.

# Project modules

# Globals and constants variables.

class PhaseMap(object):
    def __init__(self, width, height, dilationErosion=False):
        self._width = width
        self._height = height
        self._dilationErosion = dilationErosion

        self._phases = []
        self._color = []

    def addPhase(self, phase, color):
        self._phases.append(phase)
        self._color.append(color)

    def createImage(self):
#         labels.append(name)
#         color = getRGB("blue")
#         patches.append(matplotlib.patches.Patch(color=color))
        pass

    def getImage(self, gaussianFilter=False):
        imageData = np.zeros((self._width, self._height, 3), dtype=np.float32)
        for phase, colorName in zip(self._phases, self._color):
            color = self._getRGB(colorName)
            data = phase.getData(color, self._dilationErosion)
            imageData += data

        image = Image.fromarray(np.uint8(imageData*255.0))
        if gaussianFilter:
            imageFiltered = ndimage.gaussian_filter(image, sigma=(1, 1, 0), mode = 'nearest', order=0)
            image = Image.fromarray(imageFiltered)

        return image

    def getNoPhaseImage(self):
        color = (1, 1, 1)
        imageData = np.zeros((self._width, self._height, 3), dtype=np.float32)
        for phase in self._phases:
            data = phase.getData(color, self._dilationErosion)
            imageData += data

        image = Image.fromarray(np.uint8(imageData*255.0))

        return image

    def getOverlapPhaseImage(self):
        color = (1, 1, 1)
        imageData = np.zeros((self._width, self._height, 3), dtype=np.float32)
        for phase in self._phases:
            data = phase.getData(color, self._dilationErosion)
            imageData += data

        logging.debug(imageData.shape)

        logging.debug(np.min(imageData))
        logging.debug(np.max(imageData))

        mask = imageData > 1
        logging.debug(np.min(mask))
        logging.debug(np.max(mask))

        imageData[~mask] = 0

        logging.debug(np.min(imageData))
        logging.debug(np.max(imageData))

        image = Image.fromarray(np.uint8(imageData*255.0))

        return image

    def getLegend(self):
        patches = []
        labels = []

        for phase, colorName in zip(self._phases, self._color):
            labels.append(phase.name)
            color = self._getRGB(colorName)
            if color == (1, 1, 1):
                patches.append(matplotlib.patches.Patch(edgecolor='black', facecolor='white'))
            else:
                patches.append(matplotlib.patches.Patch(color=color))

        return patches, labels

    def _getRGB(self, name):
        rgb = matplotlib.colors.hex2color(matplotlib.colors.cnames[name])
        return rgb

    def saveImage(self, filepath, gaussianFilter=False):
        image = self.getImage(gaussianFilter)
        image.save(filepath)

    def showImage(self, filepath, gaussianFilter=False, legend=None):
        image = self.getImage(gaussianFilter)

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        if legend is None:
            patches, labels = self.getLegend()
        else:
            patches, labels = legend
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(filepath)

    def createNoPhaseImage(self, filepath):
        image = self.getNoPhaseImage()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(color="black"), matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["No phase", "Phases"]
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(filepath)

    def createOverlapPhaseImage(self, filepath):
        image = self.getOverlapPhaseImage()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["Overlap phases"]
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(filepath)

if __name__ == '__main__': #pragma: no cover
    import pyHendrixDemersTools.Runner as Runner
    Runner.Runner().run(runFunction=None)
