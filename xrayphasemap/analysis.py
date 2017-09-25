#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

IMAGE_WIDTH = "width"
IMAGE_HEIGHT = "height"

class PhaseAnalysis(object):
    def __init__(self, project_filepath):
        self.h5file_path = project_filepath

        self.overwrite = False

        create_color_maps()
        self.cm = plt.cm.get_cmap('YlOrRd')

    def get_width_height(self):
        h5file = self._open_hdf5_file()
        return h5file.attrs.get(IMAGE_WIDTH), h5file.attrs.get(IMAGE_HEIGHT)

    def read_element_data(self, data_type, label, file_path):
        self._read_project_file(data_type, label, file_path)


    def read_micrograph_data(self, micrograph_type, file_path):
        data = _read_data(file_path)
        logging.debug(np.min(data))
        logging.debug(np.max(data))

        h5file = self._open_hdf5_file()

        if GROUP_MICROGRAPH not in h5file:
            group_name = "/{}".format(GROUP_MICROGRAPH)
            data_type_group = h5file.create_group(group_name)
        else:
            data_type_group = h5file[GROUP_MICROGRAPH]

        logging.debug(data_type_group.name)
        logging.debug(data_type_group.parent)
        if micrograph_type not in data_type_group:
            dataset = data_type_group.create_dataset(micrograph_type, data.shape, dtype=np.float32)
            dataset[:,:] = data
            logging.debug(dataset)
            h5file.flush()
        else:
            dataset = data_type_group[micrograph_type]
            dataset[:, :] = data
            logging.debug(dataset)
            h5file.flush()

        h5file.close()

    def _read_project_file(self, data_type, label, file_path):
        h5file = self._open_hdf5_file()

        if data_type not in h5file:
            group_name = "/{}".format(data_type)
            data_type_group = h5file.create_group(group_name)
        else:
            data_type_group = h5file[data_type]

        logging.debug(data_type_group.name)
        logging.debug(data_type_group.parent)

        if label not in data_type_group:
            try:
                element_data = _read_data(file_path)
                w, h = element_data.shape
                dataset = data_type_group.create_dataset(label, element_data.shape, dtype=np.float32)
                dataset[:, :] = element_data
                logging.debug(dataset)
                h5file.flush()
            except ValueError as message:
                logging.error("%s for file_path %s", message, file_path)
            except IOError:
                logging.warning("File path does not exist %s", file_path)

        else:
            dataset = data_type_group[label]
            element_data = np.array(dataset)
            w, h = element_data.shape

        h5file.attrs[IMAGE_WIDTH] = w
        h5file.attrs[IMAGE_HEIGHT] = h

        h5file.close()


    def _open_hdf5_file(self):
        if self.overwrite:
            h5file = h5py.File(self.h5file_path, 'w')
        else:
            h5file = h5py.File(self.h5file_path, 'a')

        return h5file

    def display_histogram_one(self, data_type, label, num_bins=50, display_now=True):
        with h5py.File(self.h5file_path, 'r') as h5file:
            element_data = _get_data(h5file, data_type)

            data = element_data[label]
            _figure = self._create_histogram_figure(data_type, label, data, num_bins=num_bins)

            if display_now:
                show()

    def save_histogram_one(self, data_type, label, figure_path, num_bins=50, display_now=True):
        with h5py.File(self.h5file_path, 'r') as h5file:
            element_data = _get_data(h5file, data_type)

            data = element_data[label]
            figure = self._create_histogram_figure(data_type, label, data, num_bins=num_bins)

            file_name = "Histogram_%s_%s.png" % (data_type, label)
            file_path = os.path.join(figure_path, file_name)
            figure.savefig(file_path)
            plt.close()

    def display_histogram_all(self, data_type=None, num_bins=50, display_now=True):
        with h5py.File(self.h5file_path, 'r') as h5file:
            if data_type is None:
                for dataTypeGroup in h5file:
                    for label in h5file[dataTypeGroup]:
                        data = h5file[dataTypeGroup][label][...]
                        _figure = self._create_histogram_figure(dataTypeGroup, label, data, num_bins=num_bins)
            else:
                dataTypeGroup = h5file[data_type]
                for label in dataTypeGroup:
                    data = dataTypeGroup[label][...]
                    _figure = self._create_histogram_figure(data_type, label, data, num_bins=num_bins)

        if display_now:
            show()

    def save_histogram_all(self, figure_path, data_type=None, num_bins=50, display_now=True, color_map_name='YlOrRd'):
        with h5py.File(self.h5file_path, 'r') as h5file:
            if data_type is None:
                for data_type in h5file:
                    for label in h5file[data_type]:
                        data = h5file[data_type][label][...]
                        figure = self._create_histogram_figure(data_type, label, data, num_bins=num_bins, color_map_name=color_map_name)

                        file_name = "Histogram_%s_%s.png" % (data_type, label)
                        file_path = os.path.join(figure_path, file_name)
                        figure.savefig(file_path)
                        plt.close()
            else:
                data_type_group = h5file[data_type]
                for label in data_type_group:
                    data = data_type_group[label][...]
                    figure = self._create_histogram_figure(data_type, label, data, num_bins=num_bins, color_map_name=color_map_name)

                    file_name = "Histogram_%s_%s.png" % (data_type, label)
                    file_path = os.path.join(figure_path, file_name)
                    figure.savefig(file_path)
                    plt.close()

    def _create_histogram_figure(self, data_type, label, data, num_bins=50, color_map_name='YlOrRd'):
        fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(8, 4))

        title = "%s %s" % (data_type, label)
        fig.suptitle(title)

        # This is  the colormap I'd like to use.
        color_map = plt.cm.get_cmap(color_map_name)
        image = ax1.imshow(data, aspect='equal', cmap=color_map)
        ax1.axis('off')
        fig.colorbar(image)

        # Get the histogram
        Y, X = np.histogram(data, num_bins, normed=True)
        x_span = X.max() - X.min()
        C = [color_map(((x-X.min())/x_span)) for x in X]

        ax0.bar(X[1:-1], Y[1:], color=C, width=X[1]-X[0])
        # ax0.hist(data.flatten(), num_bins, normed=1, facecolor='green', alpha=0.5)
        ax0.set_xlabel('Value')
        ax0.set_ylabel('Probability')

        plt.subplots_adjust(wspace=0.2, top=0.85, bottom=0.15)

        return fig

    def display_scatter_diagram(self, data_type, label_a, label_b, num_bins=50, display_now=True):
        with h5py.File(self.h5file_path, 'r') as h5file:
            element_data = _get_data(h5file, data_type)

            data_a = element_data[label_a]
            data_b = element_data[label_b]
            _figure = self._create_scatter_diagram(data_type, label_a, label_b, data_a, data_b, num_bins=num_bins)

            if display_now:
                show()

    def _create_scatter_diagram(self, data_type, label_a, label_b, data_a, data_b, num_bins=50, color_map_name='YlOrRd'):
        fig, (ax0, ax1) = plt.subplots(ncols=2, figsize=(8, 4))

        label = "{}-{}".format(label_a, label_b)
        title = "%s %s" % (data_type, label)
        fig.suptitle(title)

        # This is  the colormap I'd like to use.
        x = data_a.flatten()
        y = data_b.flatten()
        minimum = 0.04
        range = [[minimum, 1.0], [minimum, 1.0]]

        color_map = plt.cm.get_cmap(color_map_name)
        counts, xedges, yedges, image = ax1.hist2d(x, y, range=range, bins=num_bins, cmap=color_map)
        fig.colorbar(image)
        ax1.set_xlabel(label_a)
        ax1.set_ylabel(label_b)

        # Get the histogram
        # Y, X = np.histogram(data, num_bins, normed=True)
        # x_span = X.max() - X.min()
        # C = [color_map(((x-X.min())/x_span)) for x in X]

        ax0.plot(data_a.flatten(), data_b.flatten(), '.')
        # ax0.hist(data.flatten(), num_bins, normed=1, facecolor='green', alpha=0.5)
        ax0.set_xlabel(label_a)
        ax0.set_ylabel(label_b)

        plt.subplots_adjust(wspace=0.2, top=0.85, bottom=0.15)

        return fig

    def save_map_all(self, figures_path, data_type=None, display_now=True, color_map_name='YlOrRd'):
        with h5py.File(self.h5file_path, 'r') as h5file:
            if data_type is None:
                for data_type in h5file:
                    for label in h5file[data_type]:
                        data_type_group = h5file[data_type]
                        data = data_type_group[label][...]
                        figure = self._create_map_figure(data_type, label, data, color_map_name)

                        file_name = "map_%s_%s.png" % (data_type, label)
                        file_path = os.path.join(figures_path, file_name)
                        figure.savefig(file_path)
                        plt.close()
            else:
                data_type_group = h5file[data_type]
                for label in data_type_group:
                    data = data_type_group[label][...]
                    figure = self._create_map_figure(data_type, label, data, color_map_name)

                    file_name = "map_%s_%s.png" % (data_type_group, label)
                    file_path = os.path.join(figures_path, file_name)
                    figure.savefig(file_path)
                    plt.close()

    def _create_map_figure(self, data_type_group, label, data, color_map_name='YlOrRd'):
        fig, ax0 = plt.subplots()

        title = "%s %s" % (data_type_group, label)
        fig.suptitle(title)

        color_map = plt.cm.get_cmap(color_map_name)
        # This is  the colormap I'd like to use.
        image = ax0.imshow(data, aspect='equal', cmap=color_map)
        ax0.axis('off')
        fig.colorbar(image)

        return fig

    def save_map_tiff(self, data_type, label, figures_path, color):
        cm = plt.get_cmap(color)
        with h5py.File(self.h5file_path, 'r') as h5file:
            data_type_group = h5file[data_type]

            data = data_type_group[label][...]

            filename = "map_%s_%s.tif" % (data_type, label)
            file_path = os.path.join(figures_path, filename)
            plt.imsave(file_path, data, cmap=cm)

    def save_micrographs_tif(self, graphic_path, basename):
        with h5py.File(self.h5file_path, 'r') as h5file:
            data_type_group = h5file[GROUP_MICROGRAPH]

            for micrographType in data_type_group:
                data = data_type_group[micrographType][...]

                image = Image.fromarray(np.uint8(data*255.0/np.max(data)))
                filename = "%s_%s.png" % (basename, micrographType)
                file_path = os.path.join(graphic_path, filename)
                image.save(file_path)

    def compute_fratio(self, input_data_type, weight_type=None, filter_size=0):
        if weight_type is not None:
            output_data_type = DATA_TYPE_FRATIO + weight_type
        else:
            output_data_type = DATA_TYPE_FRATIO

        with h5py.File(self.h5file_path, 'a') as h5file:
            if output_data_type not in h5file:
                group_name = "/{}".format(output_data_type)
                data_type_group = h5file.create_group(group_name)
            else:
                data_type_group = h5file[output_data_type]

            logging.info(output_data_type)

            element_data = _get_data(h5file, input_data_type)

            first_element = list(element_data.values())[0]
            total_intensity = np.zeros_like(first_element)

            for label in element_data:
                total_intensity += element_data[label]

            logging.debug(np.min(total_intensity))
            logging.debug(np.max(total_intensity))

            if weight_type is not None:
                weight = h5file[GROUP_MICROGRAPH][weight_type][...]
                weight /= np.max(weight)
            else:
                weight = 1.0

            for label in element_data:
                if label not in data_type_group:
                    dataset = data_type_group.create_dataset(label, total_intensity.shape, dtype=np.float32)
                else:
                    dataset = data_type_group[label]

                data = weight*element_data[label] / total_intensity
                data[np.isnan(data)] = 0
                logging.debug(np.max(data))

                if filter_size > 0:
                    data = ndimage.median_filter(data, size=filter_size)

                dataset[:, :] = data

    def compute_total_peak_intensity(self, input_data_type):
        output_data_type = GROUP_MICROGRAPH

        with h5py.File(self.h5file_path, 'a') as h5file:
            if output_data_type not in h5file:
                group_name = "/{}".format(output_data_type)
                data_type_group = h5file.create_group(group_name)
            else:
                data_type_group = h5file[output_data_type]

            element_data = _get_data(h5file, input_data_type)

            total_intensity = np.zeros_like(element_data[self.elements[0]])

            for symbol in self.elements:
                if symbol in element_data:
                    total_intensity += element_data[symbol]

            logging.debug(np.min(total_intensity))
            logging.debug(np.max(total_intensity))

            total_intensity = (total_intensity - np.min(total_intensity))  / (np.max(total_intensity) - np.min(total_intensity))

            if DATA_TYPE_TOTAL_PEAK_INTENSITY not in data_type_group:
                dataset = data_type_group.create_dataset(DATA_TYPE_TOTAL_PEAK_INTENSITY, total_intensity.shape, dtype=np.float32)
            else:
                dataset = data_type_group[DATA_TYPE_TOTAL_PEAK_INTENSITY]
            dataset[:, :] = total_intensity

    def compute_element_ratio(self, input_data_type):
        output_data_type = DATA_TYPE_ELEMENT_RATIO

        with h5py.File(self.h5file_path, 'a') as h5file:
            if output_data_type not in h5file:
                group_name = "/{}".format(output_data_type)
                data_type_group = h5file.create_group(group_name)
            else:
                data_type_group = h5file[output_data_type]

            logging.info(output_data_type)

            element_data = _get_data(h5file, input_data_type)

            for label_A in element_data:
                for label_B in element_data:
                    if label_A is not label_B:
                        label_A_B = "%s_%s" % (label_A, label_B)
                        if label_A_B not in data_type_group:
                            dataset = data_type_group.create_dataset(label_A_B, element_data[label_A].shape, dtype=np.float32)
                        else:
                            dataset = data_type_group[label_A_B]

                        data = element_data[label_A] / element_data[label_B]
                        data[np.isnan(data)] = 0
                        logging.info(np.max(data))
                        logging.info(np.min(data))
                        dataset[:, :] = data

    def get_data(self, data_type, label):
        with h5py.File(self.h5file_path, 'r') as h5file:
            data_type_group = h5file[data_type]

            data = data_type_group[label][...]

            return data

    def get_element_data(self, data_type):
        with h5py.File(self.h5file_path, 'r') as h5file:
            element_data = _get_data(h5file, data_type)

        return element_data

    def get_phase_data(self, phases, color, is_dilation_erosion=False, union=True):
        """
        """
        width, height = self.get_width_height()
        rgb_R = np.zeros((width, height), dtype=np.float32)
        rgb_G = np.zeros((width, height), dtype=np.float32)
        rgb_B = np.zeros((width, height), dtype=np.float32)

        compound_index = self.compute_compound_index(phases, is_dilation_erosion, union)

        rgb_R[compound_index] = color[0]
        rgb_G[compound_index] = color[1]
        rgb_B[compound_index] = color[2]
        data = np.dstack((rgb_R, rgb_G, rgb_B))

        return data

    def get_phase_fraction(self, phases, is_dilation_erosion=False, union=True):
        """
        """
        width, height = self.get_width_height()
        total_number_pixels = width*height

        compound_index = self.compute_compound_index(phases, is_dilation_erosion, union)

        number_pixels = np.sum(compound_index)
        phase_fraction = number_pixels/total_number_pixels
        return phase_fraction

    def compute_compound_index(self, phases, is_dilation_erosion, union):
        width, height = self.get_width_height()
        compound_index = np.zeros((width, height), dtype='bool')

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
            structure = ndimage.generate_binary_structure(2, 2)

            compound_index = ndimage.binary_closing(compound_index, structure, iterations=1)
            compound_index = ndimage.binary_opening(compound_index, structure, iterations=1)
            compound_index = ndimage.binary_closing(compound_index, structure, iterations=2)
            compound_index = ndimage.binary_opening(compound_index, structure, iterations=2)
            compound_index = ndimage.binary_closing(compound_index, structure, iterations=1)

        return compound_index

    def compute_phase_compound_index(self, phase):
        width, height = self.get_width_height()
        compound_index = np.ones((width, height), dtype='bool')

        for data_type, label in phase.conditions:
            data = self.get_data(data_type, label)
            threshold_min, threshold_max = phase.conditions[(data_type, label)]
            compound_index &= data >= threshold_min
            compound_index &= data <= threshold_max

        return compound_index


def _get_data(h5file, data_type):
    data_type_group = h5file[data_type]

    element_data = {}
    for label in data_type_group:
        element_data[label] = data_type_group[label][...]

    return element_data


def show():
    plt.show()


def _read_data_from_image_file(file_name):
    image = Image.open(file_name)
    image_data = np.array(image)
    return image_data


def _read_data_from_tsv_file(file_path):
    text = open(file_path, "rb").read()
    lines = text.split(b'\r')
    number_columns = len(lines[0].strip().split(b'\t'))
    number_rows = len(lines) - 1
    data = np.loadtxt(open(file_path, "r"))
    print(number_columns, number_rows)
    print(data.shape)
    print(data.size)
    data.shape = (number_rows, number_columns)
    return data


def _read_data_from_text_file(file_path):
    data = np.loadtxt(open(file_path, "r"), delimiter=";")
    return data


def _read_data(file_path):
    _basename, extension = os.path.splitext(file_path)
    if extension == ".tif":
        return _read_data_from_image_file(file_path)
    elif extension == ".txt":
        return _read_data_from_text_file(file_path)
    elif extension == ".tsv":
        return _read_data_from_tsv_file(file_path)

    logging.error("Unknown extension %s for file_path %s", extension, file_path)


def create_color_maps():
    number_colors = 20

    color_dict = {'red': ((0.0, 0.0, 0.0),
                          (1.0, 0.0, 0.0)),
                  'green': ((0.0, 0.0, 0.0),
                            (1.0, 0.0, 0.0)),
                  'blue': ((0.0, 0.0, 0.0),
                           (1.0, 1.0, 1.0))}
    plt.register_cmap(name='cmBlue', data=color_dict, lut=number_colors)

    color_dict = {'red': ((0.0, 0.0, 0.0),
                          (1.0, 0.0, 0.0)),
                  'green': ((0.0, 0.0, 0.0),
                            (1.0, 1.0, 1.0)),
                  'blue': ((0.0, 0.0, 0.0),
                           (1.0, 0.0, 0.0))}
    plt.register_cmap(name='cmGreen', data=color_dict, lut=number_colors)

    color_dict = {'red': ((0.0, 0.0, 0.0),
                          (1.0, 1.0, 1.0)),
                  'green': ((0.0, 0.0, 0.0),
                            (1.0, 0.0, 0.0)),
                  'blue': ((0.0, 0.0, 0.0),
                           (1.0, 0.0, 0.0))}
    plt.register_cmap(name='cmRed', data=color_dict, lut=number_colors)

    color_dict = {'red': ((0.0, 0.0, 0.0),
                          (1.0, 1.0, 1.0)),
                  'green': ((0.0, 0.0, 0.0),
                            (1.0, 0.0, 1.0)),
                  'blue': ((0.0, 0.0, 0.0),
                           (1.0, 1.0, 1.0))}
    plt.register_cmap(name='cmPink', data=color_dict, lut=number_colors)
