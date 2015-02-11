#!/usr/bin/env python
"""
.. py:currentmodule:: test_phase
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module `phase`.
"""

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Jan 19, 2015"
__copyright__ = "Copyright (c) 2015 Hendrix Demers"
__license__ = "GPL 3"

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.

# Project modules
import phase

# Globals and constants variables.

class Testphase(unittest.TestCase):
    """
    TestCase class for the module `phase`.
    """

    def setUp(self):
        """
        Setup method.
        """

        unittest.TestCase.setUp(self)

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
        self.assert_(True)

if __name__ == '__main__':  #pragma: no cover
    import nose
    import sys
    argv = sys.argv
    argv.append("--cover-package=phase")
    nose.runmodule(argv=argv)
