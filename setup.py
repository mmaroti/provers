#!/usr/bin/env python3
# Copyright (C) 2019, Miklos Maroti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
import subprocess


class BuildPy(build_py):
    def run(self):
        subprocess.call(['make', 'prover9'], cwd='provers/bin')
        #subprocess.call(['make', 'vampire'], cwd='provers/bin')
        #subprocess.call(['make', 'eprover'], cwd='provers/bin')
        build_py.run(self)


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(
    name='provers',
    packages=['provers'],
    license='GPL 3',
    url="https://github.com/mmaroti/provers",
    author="Miklos Maroti",
    author_email="mmaroti@gmail.com",
    description="Library to access different theorem provers",
    long_description=open('README.md').read(),
    python_requires='>=3.5',
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'provers = provers.util:run',
        ]
    },
    cmdclass={
        'build_py': BuildPy,
    },
    distclass=BinaryDistribution,
    package_data={
        'provers': [
            'bin/isofilter',
            'bin/interpformat',
            'bin/prooftrans',
            'bin/tptp_to_ladr',
            'bin/ladr_to_tptp',
            'bin/mace4',
            'bin/prover9',
            'bin/vampire',
            'bin/eprover',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',

    ],
    keywords='tptp logic theorem prover',
)
