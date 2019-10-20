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

import os
import re
import subprocess
import sys


def get_solver_path(command):
    command2 = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'bin', command)
    return command2 if os.path.isfile(command2) else command


def get_solver_version(command, prefix):
    try:
        p = subprocess.Popen([get_solver_path(command)], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        m = re.match('^(?:[^\n]*\n)*(' + prefix + '[^\n]*)\n',
                     p.communicate()[0].decode('ascii'))
        return m.group(1) if m else "unknown"
    except FileNotFoundError:
        return "not installed"


def print_versions():
    from . import __version__

    print("python version:", sys.version.replace('\n', ' '))
    print("provers version:", __version__)
    print("prover9 version:", get_solver_version('prover9', 'Prover9'))
    print("mace4 version:", get_solver_version('mace4', 'Mace4'))
