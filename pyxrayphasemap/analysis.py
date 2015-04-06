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
DATA_TYPE_RAW_INTENSITY = "Raw Intensity"
DATA_TYPE_NET_INTENSITY = "Net Intensity"

DATA_TYPE_FRATIO = "f-ratio"
DATA_TYPE_SE = "SE"
DATA_TYPE_BSE = "BSE"
DATA_TYPE_TOTAL_PEAK_INTENSITY = "Total peak intensity"

GROUP_MICROGRAPH = "micrograph"

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

    def readMicrographData(self, dataPath, sampleName, filename, micrographType):
        filepath = os.path.join(dataPath, filename)
        data = self._readData(filepath)
        logging.debug(np.min(data))
        logging.debug(np.max(data))

        data = (data - 26.25)  / (889.50 - 26.25)

        h5file = self._open_hdf5_file(dataPath, sampleName)

        if GROUP_MICROGRAPH not in h5file:
            groupName = "/%s" % (GROUP_MICROGRAPH)
            dataTypeGroup = h5file.create_group(groupName)
        else:
            dataTypeGroup = h5file[GROUP_MICROGRAPH]

        logging.debug(dataTypeGroup.name)
        logging.debug(dataTypeGroup.parent)
        if micrographType not in dataTypeGroup:
            dset = dataTypeGroup.create_dataset(micrographType, data.shape, dtype=np.float32)
            dset[:,:] = data
            logging.debug(dset)
            h5file.flush()
        else:
            dset = dataTypeGroup[micrographType]
            dset[:,:] = data
            logging.debug(dset)
            h5file.flush()

        h5file.close()

    def _readProjectFile(self, elements, sampleName, dataType, dataPath, filenames):
        h5file = self._open_hdf5_file(dataPath, sampleName)

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

    def _open_hdf5_file(self, dataPath, sampleName):
        filename = "PhaseAnalysis_sample%s.hdf5" % (sampleName)
        filepath = os.path.join(dataPath, filename)

        if not os.path.exists(dataPath):
            os.makedirs(dataPath)

        self.h5filepath = filepath
        if self.overwrite:
            h5file = h5py.File(filepath, 'w')
        else:
            h5file = h5py.File(filepath, 'a')

        return h5file

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

    def saveElementImages(self, graphicPath, basename, num_bins=50):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, self.dataType)

            for symbol in elementData:
                data = elementData[symbol]
                self._createFigure(graphicPath, basename, symbol, data, num_bins)

    def saveMicrographs(self, graphicPath, basename, num_bins=50):
        with h5py.File(self.h5filepath, 'r') as h5file:
            dataTypeGroup = h5file[GROUP_MICROGRAPH]

            for micrographType in dataTypeGroup:
                data = dataTypeGroup[micrographType][...]
                self._createFigure(graphicPath, basename, micrographType, data, num_bins)

    def _createFigure(self, graphicPath, basename, symbol, data, num_bins=50):
        fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(8, 4))

        title = "%s %s" % (basename, symbol)
        fig.suptitle(title)

        # This is  the colormap I'd like to use.
        cm = plt.cm.get_cmap('hot')
        image = ax1.imshow(data, aspect='equal', cmap=cm)
        ax1.axis('off')
        fig.colorbar(image)

        # Get the histogramp
        Y, X = np.histogram(data, num_bins, normed=1)
        x_span = X.max() - X.min()
        C = [cm(((x-X.min())/x_span)) for x in X]

        ax0.bar(X[1:-1], Y[1:], color=C, width=X[1]-X[0])
        #ax0.hist(data.flatten(), num_bins, normed=1, facecolor='green', alpha=0.5)
        ax0.set_xlabel('Value')
        ax0.set_ylabel('Probability')

        plt.subplots_adjust(wspace=0.2, top=0.85, bottom=0.15)

        filename = "%s_%s.png" % (basename, symbol)
        filepath = os.path.join(graphicPath, filename)
        plt.savefig(filepath)
        plt.close()

    def saveMicrographs_tif(self, graphicPath, basename):
        with h5py.File(self.h5filepath, 'r') as h5file:
            dataTypeGroup = h5file[GROUP_MICROGRAPH]

            for micrographType in dataTypeGroup:
                data = dataTypeGroup[micrographType][...]

                image = Image.fromarray(np.uint8(data*255.0/np.max(data)))
                filename = "%s_%s.png" % (basename, micrographType)
                filepath = os.path.join(graphicPath, filename)
                image.save(filepath)

    def computeFratio(self, inputDatatype, weightType=None):
        if weightType is not None:
            outputDatatype = DATA_TYPE_FRATIO + weightType
        else:
            outputDatatype = DATA_TYPE_FRATIO

        with h5py.File(self.h5filepath, 'a') as h5file:
            if outputDatatype not in h5file:
                groupName = "/%s" % (outputDatatype)
                dataTypeGroup = h5file.create_group(groupName)
            else:
                dataTypeGroup = h5file[outputDatatype]

            logging.info(outputDatatype)

            elementData = self._getData(h5file, inputDatatype)

            totalIntensity = np.zeros_like(elementData[self.elements[0]])

            for symbol in self.elements:
                totalIntensity += elementData[symbol]

            logging.debug(np.min(totalIntensity))
            logging.debug(np.max(totalIntensity))

            if weightType is not None:
                weight = h5file[GROUP_MICROGRAPH][weightType][...]
                weight /= np.max(weight)
            else:
                weight = 1.0

            for symbol in self.elements:
                if symbol not in dataTypeGroup:
                    dset = dataTypeGroup.create_dataset(symbol, totalIntensity.shape, dtype=np.float32)
                else:
                    dset = dataTypeGroup[symbol]

                data = weight*elementData[symbol] / totalIntensity
                data[np.isnan(data)] = 0
                logging.debug(np.max(data))
                dset[:,:] = data

    def computeTotalPeakIntensity(self, inputDatatype):
        outputDatatype = GROUP_MICROGRAPH

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

            logging.debug(np.min(totalIntensity))
            logging.debug(np.max(totalIntensity))

            totalIntensity = (totalIntensity - np.min(totalIntensity))  / (np.max(totalIntensity) - np.min(totalIntensity))

            if DATA_TYPE_TOTAL_PEAK_INTENSITY not in dataTypeGroup:
                dset = dataTypeGroup.create_dataset(DATA_TYPE_TOTAL_PEAK_INTENSITY, totalIntensity.shape, dtype=np.float32)
            else:
                dset = dataTypeGroup[DATA_TYPE_TOTAL_PEAK_INTENSITY]
            dset[:,:] = totalIntensity

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
