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
from setuptools import setup

# Local modules.

# Project modules

# Globals and constants variables.

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Pillow',
    'numpy',
    'scipy',
    'h5py',
    'matplotlib'
]

test_requirements = [
    'nose', 'coverage'
]

setup(name="pyphasemap",
      version='0.3.0',
      description="Create phase map from x-ray elemental maps.",
      long_description=readme + '\n\n' + history,
      author="Hendrix Demers",
      author_email="hendrix.demers@mail.mcgill.ca",
    url='https://github.com/drix00/xrayphasemap',
    packages=[
        'xrayphasemap',
    ],
    package_dir={'xrayphasemap':
                 'xrayphasemap'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='xrayphasemap',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering'],

    test_suite='tests',
    tests_require=test_requirements
      )
