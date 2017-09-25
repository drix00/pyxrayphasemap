#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: map

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Map used in the phase analysis module.
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
import logging
import os.path
import csv

# Third party modules.
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import matplotlib
import matplotlib.pyplot as plt

# Local modules.

# Project modules

# Globals and constants variables.


class PhaseMap(object):
    def __init__(self, phase_map_name, phase_analysis, is_dilation_erosion=False):
        self.phase_map_name = phase_map_name
        self.phase_analysis = phase_analysis
        self.is_dilation_erosion = is_dilation_erosion

        self.phases = {}

    def add_phase(self, phase, color_name, label=None):
        if label is None:
            label = phase.name
        self.phases[label] = ([phase], color_name, True)

    def add_phases(self, label, phases, color_name, union=True):
        self.phases[label] = (phases, color_name, union)

    def display_map(self, label=None, use_gaussian_filter=False, legend=None, display_now=True):
        image = self.get_image(label)

        plt.figure()
        if label is not None:
            plt.title(label)
        plt.imshow(image, aspect='equal')
        plt.axis('off')

        if label is None:
            if legend is None:
                patches, labels = self.get_legend()
            else:
                patches, labels = legend
            plt.figlegend(patches, labels, 'upper right')

        if display_now:
            self.show()

    def display_no_phase_map(self, display_now=True):
        image = self.get_no_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(color="black"),
                   matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["No phase", "Phases"]
        plt.figlegend(patches, labels, 'upper right')

        if display_now:
            self.show()

    def display_overlap_map(self, display_now=True):
        image = self.get_overlap_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["Overlap phases"]
        plt.figlegend(patches, labels, 'upper right')

        if display_now:
            self.show()

    def show(self):
        plt.show()

    def save_map(self, figures_path, label=None, use_gaussian_filter=False, legend=None):
        image = self.get_image(label)

        plt.figure()
        if label is not None:
            plt.title(label)
        plt.imshow(image, aspect='equal')
        plt.axis('off')

        if label is None:
            if legend is None:
                patches, labels = self.get_legend()
            else:
                patches, labels = legend
            plt.figlegend(patches, labels, 'upper right')

        if label is None:
            label = "allphases"
        file_path = os.path.join(figures_path, self.phase_map_name + label + ".png")
        plt.savefig(file_path)
        plt.close()

    def save_no_phase_map(self, figures_path):
        image = self.get_no_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(color="black"),
                   matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["No phase", "Phases"]
        plt.figlegend(patches, labels, 'upper right')

        file_path = os.path.join(figures_path, self.phase_map_name + "_nophase" + ".png")
        plt.savefig(file_path)
        plt.close()

    def save_overlap_map(self, figures_path):
        image = self.get_overlap_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["Overlap phases"]
        plt.figlegend(patches, labels, 'upper right')

        file_path = os.path.join(figures_path, self.phase_map_name + "_overlap" + ".png")
        plt.savefig(file_path)
        plt.close()

    def save_phases_fraction(self, figures_path):
        phase_fractions = self.get_phases_fraction()

        file_path = os.path.join(figures_path, self.phase_map_name + "_phases_fraction" + ".csv")
        with open(file_path, 'w', newline='\n') as output_file:
            writer = csv.writer(output_file)

            header_row = ["Phase", "Pixel fraction"]
            writer.writerow(header_row)

            for phase_name in phase_fractions:
                row = []
                row.append(phase_name)
                row.append(phase_fractions[phase_name])
                writer.writerow(row)

    def get_image(self, label=None, use_gaussian_filter=False):
        width, height = self.phase_analysis.get_width_height()
        image_data = np.zeros((width, height, 3), dtype=np.float32)

        if label is None:
            for label in self.phases:
                phases, color_name, union = self.phases[label]
                color = self._get_rgb(color_name)
                data = self.phase_analysis.get_phase_data(phases, color, self.is_dilation_erosion, union)
                image_data += data
        else:
                phases, color_name, union = self.phases[label]
                color = self._get_rgb(color_name)
                data = self.phase_analysis.get_phase_data(phases, color, self.is_dilation_erosion, union)
                image_data += data

        image = Image.fromarray(np.uint8(image_data*255.0))
        if use_gaussian_filter:
            image_filtered = gaussian_filter(image, sigma=(1, 1, 0), mode='nearest', order=0)
            image = Image.fromarray(image_filtered)

        return image

    def get_no_phase_image(self):
        color = (1, 1, 1)
        width, height = self.phase_analysis.get_width_height()
        image_data = np.zeros((width, height, 3), dtype=np.float32)
        for label in self.phases:
            phases, _color_name, union = self.phases[label]
            data = self.phase_analysis.get_phase_data(phases, color, self.is_dilation_erosion, union)
            image_data += data

        image = Image.fromarray(np.uint8(image_data*255.0))

        return image

    def get_overlap_phase_image(self):
        color = (1, 1, 1)
        width, height = self.phase_analysis.get_width_height()
        image_data = np.zeros((width, height, 3), dtype=np.float32)
        for label in self.phases:
            phases, _color_name, union = self.phases[label]
            data = self.phase_analysis.get_phase_data(phases, color, self.is_dilation_erosion, union)
            image_data += data

        logging.debug(image_data.shape)

        logging.debug(np.min(image_data))
        logging.debug(np.max(image_data))

        mask = image_data > 1
        logging.debug(np.min(mask))
        logging.debug(np.max(mask))

        image_data[~mask] = 0

        logging.debug(np.min(image_data))
        logging.debug(np.max(image_data))

        image = Image.fromarray(np.uint8(image_data*255.0))

        return image

    def get_phases_fraction(self):
        phase_fractions = {}
        for label in self.phases:
            phases, _color_name, union = self.phases[label]
            phase_fraction = self.phase_analysis.get_phase_fraction(phases, self.is_dilation_erosion, union)

            phase_fractions[label] = phase_fraction

        return phase_fractions

    def get_legend(self):
        patches = []
        labels = []

        for label in self.phases:
            labels.append(label)
            _phase, color_name, _union = self.phases[label]
            color = self._get_rgb(color_name)
            if color == (1, 1, 1):
                patches.append(matplotlib.patches.Patch(edgecolor='black', facecolor='white'))
            else:
                patches.append(matplotlib.patches.Patch(color=color))

        return patches, labels

    def _get_rgb(self, name):
        rgb = matplotlib.colors.hex2color(matplotlib.colors.cnames[name])
        return rgb

    def save_image(self, file_path, use_gaussian_filter=False):
        image = self.get_image(use_gaussian_filter)
        image.save(file_path)

    def show_image(self, file_path, use_gaussian_filter=False, legend=None, save_only=False):
        image = self.get_image(use_gaussian_filter)

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        if legend is None:
            patches, labels = self.get_legend()
        else:
            patches, labels = legend
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(file_path)

        if save_only:
            plt.close()

    def create_no_phase_image(self, file_path):
        image = self.get_no_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(color="black"), matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["No phase", "Phases"]
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(file_path)

    def create_overlap_phase_image(self, file_path):
        image = self.get_overlap_phase_image()

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        patches = [matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
        labels = ["Overlap phases"]
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(file_path)


def save_phase_only(phase_map, phase, graphic_path, color):
    """
    Save an png image of one phase.

    .. todo:: Find why the parameter is phase_map, should we pass the width and height only?

    :param phase_map: get the width and height of the image
    :param phase: phase object to create a image
    :param graphic_path: path to save the image
    :param color: color to use for the image

    """
    phase_image = PhaseMap(phase_map.width, phase_map.height)

    phase_image.add_phase(phase, color)
    filename = r'%s_%s_%s.png' % (phase_map.sampleName, phase_map.dataType, phase.name)
    file_path = os.path.join(graphic_path, filename)
    phase_image.save_image(file_path)
