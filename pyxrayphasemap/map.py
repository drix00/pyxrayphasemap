#!/usr/bin/env python
"""
.. py:currentmodule:: pyxrayphasemap.map
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
import os.path

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
    def __init__(self, phase_map_name, phase_analysis):
        self.phase_map_name = phase_map_name
        self.phase_analysis = phase_analysis
        
        self.phases = {}

    def add_phase(self, phase, color_name, label=None):
        if label is None:
            label = phase.name
        self.phases[label] = (phase, color_name)

    def display_map(self, label=None, gaussianFilter=False, legend=None, display_now=True):
        image = self.get_image(label)
        
        plt.figure()
        if label is not None:
            plt.title(label)
        plt.imshow(image, aspect='equal')
        plt.axis('off')
        
        if label is None:
            if legend is None:
                patches, labels = self.getLegend()
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

        patches = [matplotlib.patches.Patch(color="black"), matplotlib.patches.Patch(edgecolor='black', facecolor='white')]
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

    def get_image(self, label=None, gaussianFilter=False):
        width = self.phase_analysis.width
        height = self.phase_analysis.height
        imageData = np.zeros((width, height, 3), dtype=np.float32)
        
        if label is None:
            for label in self.phases:
                phase, color_name = self.phases[label]
                color = self._getRGB(color_name)
                data = self.phase_analysis.get_phase_data(phase, color)
                imageData += data
        else:
                phase, color_name = self.phases[label]
                color = self._getRGB(color_name)
                data = self.phase_analysis.get_phase_data(phase, color)
                imageData += data
            
        image = Image.fromarray(np.uint8(imageData*255.0))
        if gaussianFilter:
            imageFiltered = ndimage.gaussian_filter(image, sigma=(1, 1, 0), mode = 'nearest', order=0)
            image = Image.fromarray(imageFiltered)

        return image

    def get_no_phase_image(self):
        color = (1, 1, 1)
        width = self.phase_analysis.width
        height = self.phase_analysis.height
        imageData = np.zeros((width, height, 3), dtype=np.float32)
        for label in self.phases:
            phase, _color_name = self.phases[label]
            data = self.phase_analysis.get_phase_data(phase, color)
            imageData += data

        image = Image.fromarray(np.uint8(imageData*255.0))

        return image

    def get_overlap_phase_image(self):
        color = (1, 1, 1)
        width = self.phase_analysis.width
        height = self.phase_analysis.height
        imageData = np.zeros((width, height, 3), dtype=np.float32)
        for label in self.phases:
            phase, _color_name = self.phases[label]
            data = self.phase_analysis.get_phase_data(phase, color)
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

        for label in self.phases:
            labels.append(label)
            _phase, color_name = self.phases[label]
            color = self._getRGB(color_name)
            if color == (1, 1, 1):
                patches.append(matplotlib.patches.Patch(edgecolor='black', facecolor='white'))
            else:
                patches.append(matplotlib.patches.Patch(color=color))

        return patches, labels

    def _getRGB(self, name):
        rgb = matplotlib.colors.hex2color(matplotlib.colors.cnames[name])
        return rgb

    def saveImage(self, filepath, gaussianFilter=False):
        image = self.get_image(gaussianFilter)
        image.save(filepath)

    def showImage(self, filepath, gaussianFilter=False, legend=None, save_only=False):
        image = self.get_image(gaussianFilter)

        plt.figure()

        plt.imshow(image, aspect='equal')
        plt.axis('off')

        if legend is None:
            patches, labels = self.getLegend()
        else:
            patches, labels = legend
        plt.figlegend(patches, labels, 'upper right')
        plt.savefig(filepath)

        if save_only:
            plt.close()

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

def savePhaseOnly(phaseMap, phase, graphicPath, color):
    phaseImage = PhaseMap(phaseMap.width, phaseMap.height)

    phaseImage.add_phase(phase, color)
    filename= r'%s_%s_%s.png' % (phaseMap.sampleName, phaseMap.dataType, phase.name)
    filepath = os.path.join(graphicPath, filename)
    phaseImage.saveImage(filepath)
