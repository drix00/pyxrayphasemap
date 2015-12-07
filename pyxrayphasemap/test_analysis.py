#!/usr/bin/env python
"""
.. py:currentmodule:: test_analysis
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module `analysis`.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Mar 26, 2015"
__copyright__ = "Copyright (c) 2015 Hendrix Demers"
__license__ = "GPL 3"

# Standard library modules.
import unittest
import os.path

# Third party modules.

# Local modules.
import pyHendrixDemersTools.Files as Files

# Project modules
from pyxrayphasemap.analysis import PhaseAnalysis

# Globals and constants variables.

class Testanalysis(unittest.TestCase):
    """
    TestCase class for the module `analysis`.
    """

    def setUp(self):
        """
        Setup method.
        """

        unittest.TestCase.setUp(self)

        self.test_data_path = Files.getCurrentModulePath(__file__, "../test_data")

    def tearDown(self):
        """
        Teardown method.
        """

        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        """
        First test to check if the testcase is working with the testing framework.
        """

        #self.fail("Test if the testcase is working.")

    def test_test_data_path(self):
        """
        Tests for method :py:meth:`test_data_path`.
        """

        test_data_path = Files.getCurrentModulePath(__file__, "../test_data")

        self.assertTrue(os.path.isdir(test_data_path))

        #self.fail("Test if the testcase is working.")

    def test__readDataFromTextFile(self):
        """
        Tests for method :py:meth:`_readDataFromTextFile`.
        """

        phase_analysis = PhaseAnalysis("Dummy_filepath")
        filepath = os.path.join(self.test_data_path, "bruker", "good_text_export.txt")
        data = phase_analysis._readDataFromTextFile(filepath)

        print(data.shape)
        #self.fail("Test if the testcase is working.")

if __name__ == '__main__':  #pragma: no cover
    import nose
    import sys
    argv = sys.argv
    argv.append("--cover-package=pyxrayphasemap.analysis")
    nose.runmodule(argv=argv)
