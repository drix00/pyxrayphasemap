#!/usr/bin/env python
"""
.. py:currentmodule:: xrayphasemap.analysis
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Create phase map from x-ray map data.
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
import os.path
import logging

# Third party modules.
import h5py
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage

# Local modules.

# Project modules

# Globals and constants variables.
DATA_TYPE_ATOMIC_NORMALIZED = "atom norm"
DATA_TYPE_WEIGHT_NORMALIZED = "weight norm"
DATA_TYPE_INTENSITY_DECONVOLUTION = "Intensity Deconvolution"
DATA_TYPE_RAW_INTENSITY = "Raw Intensity"
DATA_TYPE_NET_INTENSITY = "Net Intensity"

DATA_TYPE_FRATIO = "f-ratio"
DATA_TYPE_ELEMENT_RATIO = "element ratio"

DATA_TYPE_SE = "SE"
DATA_TYPE_BSE = "BSE"
DATA_TYPE_TOTAL_PEAK_INTENSITY = "Total peak intensity"

GROUP_MICROGRAPH = "micrograph"

class PhaseAnalysis(object):
    def __init__(self, project_filepath):
        self.h5filepath = project_filepath

        self.overwrite = False

        self.create_color_maps()
        self.cm = plt.cm.get_cmap('YlOrRd')

        self.width = None
        self.height = None

    def create_color_maps(self):
        number_colors = 20

        cdict = {'red': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0)),

                 'green': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0)),

                 'blue': ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0))
        }
        plt.register_cmap(name='cmBlue', data=cdict, lut=number_colors)

        cdict = {'red': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0)),

                 'green': ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0)),

                 'blue': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0))
        }
        plt.register_cmap(name='cmGreen', data=cdict, lut=number_colors)

        cdict = {'red': ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0)),

                 'green': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0)),

                 'blue': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 0.0))
        }
        plt.register_cmap(name='cmRed', data=cdict, lut=number_colors)

        cdict = {'red': ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0)),

                 'green': ((0.0, 0.0, 0.0),
                         (1.0, 0.0, 1.0)),

                 'blue': ((0.0, 0.0, 0.0),
                         (1.0, 1.0, 1.0))
        }
        plt.register_cmap(name='cmPink', data=cdict, lut=number_colors)

    def readElementData(self, data_type, label, filepath):
        self.width, self.height = self._readProjectFile(data_type, label, filepath)

    def readMicrographData(self, micrograph_type, filepath):
        data = self._readData(filepath)
        logging.debug(np.min(data))
        logging.debug(np.max(data))

        h5file = self._open_hdf5_file()

        if GROUP_MICROGRAPH not in h5file:
            groupName = "/%s" % (GROUP_MICROGRAPH)
            dataTypeGroup = h5file.create_group(groupName)
        else:
            dataTypeGroup = h5file[GROUP_MICROGRAPH]

        logging.debug(dataTypeGroup.name)
        logging.debug(dataTypeGroup.parent)
        if micrograph_type not in dataTypeGroup:
            dset = dataTypeGroup.create_dataset(micrograph_type, data.shape, dtype=np.float32)
            dset[:,:] = data
            logging.debug(dset)
            h5file.flush()
        else:
            dset = dataTypeGroup[micrograph_type]
            dset[:,:] = data
            logging.debug(dset)
            h5file.flush()

        h5file.close()

    def _readProjectFile(self, data_type, label, filepath):
        h5file = self._open_hdf5_file()

        if data_type not in h5file:
            groupName = "/%s" % (data_type)
            dataTypeGroup = h5file.create_group(groupName)
        else:
            dataTypeGroup = h5file[data_type]

        logging.debug(dataTypeGroup.name)
        logging.debug(dataTypeGroup.parent)

        if label not in dataTypeGroup:
            try:
                elementData = self._readData(filepath)
                w, h = elementData.shape
                dset = dataTypeGroup.create_dataset(label, elementData.shape, dtype=np.float32)
                dset[:,:] = elementData
                logging.debug(dset)
                h5file.flush()
            except ValueError as message:
                logging.error("%s for filepath %s", message, filepath)
            except IOError:
                logging.warning("Filepath does not exist %s", filepath)

        else:
            dset = dataTypeGroup[label]
            elementData = np.array(dset)
            w, h = elementData.shape

        h5file.close()

        return w, h

    def _open_hdf5_file(self):
        if self.overwrite:
            h5file = h5py.File(self.h5filepath, 'w')
        else:
            h5file = h5py.File(self.h5filepath, 'a')

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
        data = np.loadtxt(open(filepath,"r"),delimiter=";")
        return data

    def _readDataFromTSVFile(self, filepath):
        text = open(filepath,"rb").read()
        lines = text.split(b'\r')
        numberColumns = len(lines[0].strip().split(b'\t'))
        numberRows = len(lines) - 1
        data = np.loadtxt(open(filepath,"r"))
        print(numberColumns, numberRows)
        print(data.shape)
        print(data.size)
        data.shape = (numberRows, numberColumns)
        return data

    def _readDataFromImageFile(self, Filename):
        Im = Image.open(Filename)
        arr = np.array(Im)
        return arr

    def show(self):
        plt.show()

    def display_histogram_one(self, data_type, label, num_bins=50, display_now=True):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, data_type)

            data = elementData[label]
            _figure = self._create_histogram_figure(data_type, label, data, num_bins)

            if display_now:
                self.show()

    def save_histogram_one(self, data_type, label, figure_path, num_bins=50, display_now=True):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, data_type)

            data = elementData[label]
            figure = self._create_histogram_figure(data_type, label, data, num_bins)

            filename = "Histogram_%s_%s.png" % (data_type, label)
            filepath = os.path.join(figure_path, filename)
            figure.savefig(filepath)
            plt.close()

    def display_histogram_all(self, data_type=None, num_bins=50, display_now=True):
        with h5py.File(self.h5filepath, 'r') as h5file:
            if data_type is None:
                for dataTypeGroup in h5file:
                    for label in h5file[dataTypeGroup]:
                        data = h5file[dataTypeGroup][label][...]
                        _figure = self._create_histogram_figure(dataTypeGroup, label, data, num_bins)
            else:
                dataTypeGroup = h5file[data_type]
                for label in dataTypeGroup:
                    data = dataTypeGroup[label][...]
                    _figure = self._create_histogram_figure(data_type, label, data, num_bins)

        if display_now:
            self.show()

    def save_histogram_all(self, figure_path, data_type=None, num_bins=50, display_now=True):
        with h5py.File(self.h5filepath, 'r') as h5file:
            if data_type is None:
                for dataTypeGroup in h5file:
                    for label in h5file[dataTypeGroup]:
                        data = h5file[dataTypeGroup][label][...]
                        figure = self._create_histogram_figure(dataTypeGroup, label, data, num_bins)

                        filename = "Histogram_%s_%s.png" % (dataTypeGroup, label)
                        filepath = os.path.join(figure_path, filename)
                        figure.savefig(filepath)
                        plt.close()
            else:
                dataTypeGroup = h5file[data_type]
                for label in dataTypeGroup:
                    data = dataTypeGroup[label][...]
                    figure = self._create_histogram_figure(data_type, label, data, num_bins)

                    filename = "Histogram_%s_%s.png" % (data_type, label)
                    filepath = os.path.join(figure_path, filename)
                    figure.savefig(filepath)
                    plt.close()

    def _create_histogram_figure(self, data_type, label, data, num_bins=50):
        fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(8, 4))

        title = "%s %s" % (data_type, label)
        fig.suptitle(title)

        # This is  the colormap I'd like to use.
        image = ax1.imshow(data, aspect='equal', cmap=self.cm)
        ax1.axis('off')
        fig.colorbar(image)

        # Get the histogramp
        Y, X = np.histogram(data, num_bins, normed=True)
        x_span = X.max() - X.min()
        C = [self.cm(((x-X.min())/x_span)) for x in X]

        ax0.bar(X[1:-1], Y[1:], color=C, width=X[1]-X[0])
        #ax0.hist(data.flatten(), num_bins, normed=1, facecolor='green', alpha=0.5)
        ax0.set_xlabel('Value')
        ax0.set_ylabel('Probability')

        plt.subplots_adjust(wspace=0.2, top=0.85, bottom=0.15)

        return fig

    def save_map_tiff(self, data_type, label, figures_path, color):
        cm = plt.get_cmap(color)
        with h5py.File(self.h5filepath, 'r') as h5file:
            dataTypeGroup = h5file[data_type]

            data = dataTypeGroup[label][...]

            filename = "map_%s_%s.tif" % (data_type, label)
            filepath = os.path.join(figures_path, filename)
            plt.imsave(filepath, data, cmap=cm)

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

            first_element = list(elementData.values())[0]
            totalIntensity = np.zeros_like(first_element)

            for label in elementData:
                totalIntensity += elementData[label]

            logging.debug(np.min(totalIntensity))
            logging.debug(np.max(totalIntensity))

            if weightType is not None:
                weight = h5file[GROUP_MICROGRAPH][weightType][...]
                weight /= np.max(weight)
            else:
                weight = 1.0

            for label in elementData:
                if label not in dataTypeGroup:
                    dset = dataTypeGroup.create_dataset(label, totalIntensity.shape, dtype=np.float32)
                else:
                    dset = dataTypeGroup[label]

                data = weight*elementData[label] / totalIntensity
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
                if symbol in elementData:
                    totalIntensity += elementData[symbol]

            logging.debug(np.min(totalIntensity))
            logging.debug(np.max(totalIntensity))

            totalIntensity = (totalIntensity - np.min(totalIntensity))  / (np.max(totalIntensity) - np.min(totalIntensity))

            if DATA_TYPE_TOTAL_PEAK_INTENSITY not in dataTypeGroup:
                dset = dataTypeGroup.create_dataset(DATA_TYPE_TOTAL_PEAK_INTENSITY, totalIntensity.shape, dtype=np.float32)
            else:
                dset = dataTypeGroup[DATA_TYPE_TOTAL_PEAK_INTENSITY]
            dset[:,:] = totalIntensity

    def computeElementRatio(self, inputDatatype):
        outputDatatype = DATA_TYPE_ELEMENT_RATIO

        with h5py.File(self.h5filepath, 'a') as h5file:
            if outputDatatype not in h5file:
                groupName = "/%s" % (outputDatatype)
                dataTypeGroup = h5file.create_group(groupName)
            else:
                dataTypeGroup = h5file[outputDatatype]

            logging.info(outputDatatype)

            elementData = self._getData(h5file, inputDatatype)

            for label_A in elementData:
                for label_B in elementData:
                    if label_A is not label_B:
                        label_A_B = "%s_%s" % (label_A, label_B)
                        if label_A_B not in dataTypeGroup:
                            dset = dataTypeGroup.create_dataset(label_A_B, elementData[label_A].shape, dtype=np.float32)
                        else:
                            dset = dataTypeGroup[label_A_B]

                        data = elementData[label_A] / elementData[label_B]
                        data[np.isnan(data)] = 0
                        logging.info(np.max(data))
                        logging.info(np.min(data))
                        dset[:,:] = data

    def get_data(self, data_type, label):
        with h5py.File(self.h5filepath, 'r') as h5file:
            dataTypeGroup = h5file[data_type]

            data = dataTypeGroup[label][...]

            return data

    def getElementData(self, datatype):
        with h5py.File(self.h5filepath, 'r') as h5file:
            elementData = self._getData(h5file, datatype)

        return elementData

    def _getData(self, h5file, datatype):
        dataTypeGroup = h5file[datatype]

        elementData = {}
        for label in dataTypeGroup:
            elementData[label] = dataTypeGroup[label][...]

        return elementData

    def get_phase_data(self, phases, color, is_dilation_erosion=False, union=True):
        """
        """
        rgb_R = np.zeros((self.width, self.height), dtype=np.float32)
        rgb_G = np.zeros((self.width, self.height), dtype=np.float32)
        rgb_B = np.zeros((self.width, self.height), dtype=np.float32)

        compound_index = self.compute_compound_index(phases, is_dilation_erosion, union)

        rgb_R[compound_index] = color[0]
        rgb_G[compound_index] = color[1]
        rgb_B[compound_index] = color[2]
        data = np.dstack((rgb_R, rgb_G, rgb_B))

        return data

    def get_phase_fraction(self, phases, is_dilation_erosion=False, union=True):
        """
        """
        total_number_pixels = self.width*self.height

        compound_index = self.compute_compound_index(phases, is_dilation_erosion, union)

        number_pixels = np.sum(compound_index)
        phase_fraction = number_pixels/total_number_pixels
        return phase_fraction

    def compute_compound_index(self, phases, is_dilation_erosion, union):
        compound_index = np.zeros((self.width, self.height), dtype='bool')

        try:
            phases[0]
        except TypeError:
            phases = [phases]

        for phase in phases:
            phase_compound_index = self.compute_phase_compound_index(phase)

            if union:
                compound_index |= phase_compound_index
            else:
                compound_index &= phase_compound_index

        if is_dilation_erosion:
            struct = ndimage.generate_binary_structure(2, 2)

            compound_index = ndimage.binary_closing(compound_index, struct, iterations=1)
            compound_index = ndimage.binary_opening(compound_index, struct, iterations=1)
            compound_index = ndimage.binary_closing(compound_index, struct, iterations=2)
            compound_index = ndimage.binary_opening(compound_index, struct, iterations=2)
            compound_index = ndimage.binary_closing(compound_index, struct, iterations=1)

        return compound_index

    def compute_phase_compound_index(self, phase):
        compound_index = np.ones((self.width, self.height), dtype='bool')

        for data_type, label in phase.conditions:
            data = self.get_data(data_type, label)
            thresholdMin, thresholdMax = phase.conditions[(data_type, label)]
            compound_index &= data >= thresholdMin
            compound_index &= data <= thresholdMax

        return compound_index

    @property
    def overwrite(self):
        return self._overwrite
    @overwrite.setter
    def overwrite(self, overwrite):
        self._overwrite = overwrite

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
