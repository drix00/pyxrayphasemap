#!/usr/bin/env python
"""
.. py:currentmodule:: setup
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Setup pyXRayPhaseMap project.
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
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.

# Project modules

# Globals and constants variables.

readme_file_path = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme_file_path).read() + '\n\n'

setup(name="pyxrayphasemap",
      version='0.3.0',
      description="Create phase map from x-ray elemental maps.",
      long_description=long_description,
      author="Hendrix Demers",
      author_email="hendrix.demers@mail.mcgill.ca",
      license="Apache License, Version 2.0",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: Apache License, Version 2.0',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering'],

      packages=find_packages(exclude=['gui', ]),

      include_package_data=False,  # Do not include test data

      install_requires=['Pillow',
                        'numpy',
                        'scipy',
                        'h5py',
                        'matplotlib'],
      setup_requires=['nose', 'coverage'],

      test_suite='nose.collector',
      )
