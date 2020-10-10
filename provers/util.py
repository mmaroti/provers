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


def get_program_path(command):
    command2 = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), 'bin', command)
    return command2 if os.path.isfile(command2) else command


def run_program(args, input, timeout=None):
    try:
        r = subprocess.run(
            [get_program_path(args[0])] + args[1:],
            input=str(input),
            timeout=None if timeout is None else float(timeout),
            stdout=subprocess.PIPE,
            #stderr=subprocess.STDOUT, #revert, else Mace4 produces erronous output 
            encoding='ascii')
        return r.stdout
    except subprocess.TimeoutExpired:
        return 'timeout'


def get_program_version(args, prefix):
    try:
        m = re.match('^(?:[^\n]*\n)*(' + prefix + '[^\n]*)\n',
                     run_program(args, ''))
        return m.group(1) if m else "unknown"
    except FileNotFoundError:
        return "not installed"


def print_versions():
    from . import __version__

    print("python version:", sys.version.replace('\n', ' '))
    print("provers version:", __version__)
    print("prover9 version:", get_program_version(
        ['prover9', '--version'], 'Prover9'))
    print("vampire version:", get_program_version(
        ['vampire', '--version'], 'Vampire'))
    print("eprover version:", get_program_version(
        ['eprover', '--version'], 'E'))


def run():
    args = sys.argv
    if len(args) <= 1:
        print_versions()
        return

    import os
    os.execvp(get_program_path(args[1]), args[1:])
