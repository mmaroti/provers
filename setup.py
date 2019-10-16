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

setup(
    name='provers',
    version='0.1',
    packages=['provers'],
    license='GPL 3',
    description="Library to access different different theorem provers",
    long_description=open('README.md').read(),
    # do not list standard packages
    python_requires='>=3.5',
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'provers = provers.__main__:run'
        ]
    }
)
