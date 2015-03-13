#!/usr/bin/env python
"""
.. py:currentmodule:: pyMcGill.experimental.phaseMap.PhaseAnalysis
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Create phase map from x-ray map data.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = ""
__date__ = ""
__copyright__ = "Copyright (c) 2014 Hendrix Demers"
__license__ = ""

# Standard library modules.
import os.path
import logging

# Third party modules.
import h5py
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Local modules.

# Project modules

# Globals and constants variables.
DATA_TYPE_ATOMIC_NORMALIZED = "atom norm"
DATA_TYPE_WEIGHT_NORMALIZED = "weight norm"
DATA_TYPE_INTENSITY_DECONVOLUTION = "Intensity Deconvolution"
DATA_TYPE_FRATIO = "f-ratio"

class PhaseAnalysis(object):
    def __init__(self):
        self.elements = []
        self.sampleName = None
        self.dataType = None
        self.overwrite = False
        self.dataExtension = None
        self.width = None
        self.height = None
        self.h5filepath = None

    def readElementData(self, dataPath, filenames=None):
        self.width, self.height = self._readProjectFile(self.elements, self.sampleName, self.dataType, dataPath, filenames)

    def _readProjectFile(self, elements, sampleName, dataType, dataPath, filenames):
        filename = "PhaseAnalysis_sample%s.hdf5" % (sampleName)
        filepath = os.path.join(dataPath, filename)

        if not os.path.exists(dataPath):
            os.makedirs(dataPath)

        self.h5filepath = filepath
        if self.overwrite:
            h5file = h5py.File(filepath, 'w')
        else:
            h5file = h5py.File(filepath, 'a')

        if dataType not in h5file:
            groupName = "/%s" % (dataType)
            dataTypeGroup = h5file.create_group(groupName)
        else:
            dataTypeGroup = h5file[dataType]

        logging.debug(dataTypeGroup.name)
        logging.debug(dataTypeGroup.parent)

        elementData = {}

        for element in elements:
            if element not in dataTypeGroup:
                if filenames is None:
                    filename= r'%s-%s_%s.%s' % (sampleName, dataType, element, self.dataExtension)
                    filepath = os.path.join(dataPath, filename)

                    if not os.path.isfile(filepath) and dataType == DATA_TYPE_WEIGHT_NORMALIZED:
                        filename= r'%s_%s_%s.%s' % (sampleName, "mass_norm", element, self.dataExtension)
                        filepath = os.path.join(dataPath, filename)

                    if not os.path.isfile(filepath) and dataType == DATA_TYPE_WEIGHT_NORMALIZED:
                        filename= r'%s-%s_%s.%s' % (sampleName, "w% norm", element, self.dataExtension)
                        filepath = os.path.join(dataPath, filename)

                    if not os.path.isfile(filepath) and dataType == DATA_TYPE_WEIGHT_NORMALIZED:
                        filename= r'%s-%s_%s.%s' % (sampleName, "w%-norm", element, self.dataExtension)
                        filepath = os.path.join(dataPath, filename)
                else:
                    filename= filenames[element]
                    filepath = os.path.join(dataPath, filename)

                try:
                    elementData[element] = self._readData(filepath)
                    w, h = elementData[element].shape
                    dset = dataTypeGroup.create_dataset(element, elementData[element].shape, dtype=np.float32)
                    dset[:,:] = elementData[element]
                    logging.debug(dset)
                    h5file.flush()
                except IOError:
                    logging.warning("Filepath does not exist %s", filepath)
            else:
                dset = dataTypeGroup[element]
                elementData[element] = np.array(dset)
                w, h = elementData[element].shape

        h5file.close()

        return w, h

    def _readData(self, filepath):
        _basename, extension = os.path.splitext(filepath)
        if extension == ".tif":
            return self._readDataFromImageFile(filepath)
        elif extension == ".txt":
            return self._readDataFromTextFile(filepath)
        elif extension == ".tsv":
            return self._readDataFromTSVFile(filepath)

        logging.error("Unkown extension %s for filepath %s", extension, filepath)

    def _readDataFromTextFile(self, filepath):
        data = np.loadtxt(open(filepath,"rb"),delimiter=";")
        return data

    def _readDataFromTSVFile(self, filepath):
        text = open(filepath,"rb").read()
        lines = text.split(b'\r')
        numberColumns = len(lines[0].split(b'\t'))
        numberRows = len(lines) - 1
        data = np.loadtxt(open(filepath,"rb"))
        data.shape = (numberRows, numberColumns)
        return data

    def _readDataFromImageFile(self, Filename):
        Im = Image.open(Filename)
        arr = np.array(Im)
        return arr

    def saveElementImages(self, graphicPath, basename):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, self.dataType)

            for symbol in elementData:
                data = elementData[symbol]
                plt.figure()
                title = "%s %s" % (basename, symbol)
                plt.title(title)

                plt.imshow(data, aspect='equal')
                plt.axis('off')
                plt.colorbar()

                filename = "%s_%s.png" % (basename, symbol)
                filepath = os.path.join(graphicPath, filename)
                plt.savefig(filepath)
                plt.close()

    def computeFratio(self, inputDatatype):
        outputDatatype = DATA_TYPE_FRATIO

        with h5py.File(self.h5filepath, 'a') as h5file:
            if outputDatatype not in h5file:
                groupName = "/%s" % (outputDatatype)
                dataTypeGroup = h5file.create_group(groupName)
            else:
                dataTypeGroup = h5file[outputDatatype]

            elementData = self._getData(h5file, inputDatatype)

            totalIntensity = np.zeros_like(elementData[self.elements[0]])

            for symbol in self.elements:
                totalIntensity += elementData[symbol]

            logging.info(np.min(totalIntensity))
            logging.info(np.max(totalIntensity))

            for symbol in self.elements:
                if symbol not in dataTypeGroup:
                    dset = dataTypeGroup.create_dataset(symbol, totalIntensity.shape, dtype=np.float32)
                else:
                    dset = dataTypeGroup[symbol]
                dset[:,:] = elementData[symbol] / totalIntensity

    def getElementData(self, datatype):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, datatype)

        return elementData

    def _getData(self, h5file, datatype):
        dataTypeGroup = h5file[datatype]

        elementData = {}
        for symbol in self.elements:
            elementData[symbol] = dataTypeGroup[symbol][...]

        return elementData

    @property
    def elements(self):
        return self._elements
    @elements.setter
    def elements(self, elements):
        self._elements = elements

    @property
    def sampleName(self):
        return self._sampleName
    @sampleName.setter
    def sampleName(self, sampleName):
        self._sampleName = sampleName

    @property
    def dataType(self):
        return self._dataType
    @dataType.setter
    def dataType(self, dataType):
        self._dataType = dataType

    @property
    def overwrite(self):
        return self._overwrite
    @overwrite.setter
    def overwrite(self, overwrite):
        self._overwrite = overwrite

    @property
    def dataExtension(self):
        return self._dataExtension
    @dataExtension.setter
    def dataExtension(self, dataExtension):
        self._dataExtension = dataExtension

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, width):
        self._width = width

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, height):
        self._height = height

    @property
    def h5filepath(self):
        return self._h5filepath
    @h5filepath.setter
    def h5filepath(self, h5filepath):
        self._h5filepath = h5filepath

if __name__ == '__main__': #pragma: no cover
    import pyHendrixDemersTools.Runner as Runner
    Runner.Runner().run(runFunction=None)
