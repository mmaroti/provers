#!/usr/bin/env python3
# Copyright (C) 2019, Miklos Maroti and Peter Jipsen
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

from .util import run_program
from .prover9 import Proof, Model
import re


def E(assume_list, goal_list, prover_seconds=60, info=False):
    """
    Invoke Eprover with lists of formulas and some default options

    INPUT:
        assume_list -- list of Prover9 formulas that assumptions
        goal_list -- list of Prover9 formulas that goals
        prover_seconds -- number of seconds to run Eprover
        info -- print input and output of eprover

    EXAMPLES:
        >>> E(['![X]:X=X'], ['![X]:X=X']) # trivial proof
        >>> E(['![X]:X=X'], ['![X,Y]:X=Y)']) # trivial counterexample
        >>> Grp=[
                "![X,Y,Z]: p(p(X,Y),Z) = p(X,p(Y,Z))",
                "![X]: p(e(),X) = X",
                "![X]: p(i(X),X) = e()",
            ]
        >>> E(Mon, ["![X]: p(X,i(X))=e()"])
        >>> E(Mon, ["![X,Y]: p(X,Y)=p(Y,X)"])
    """
    in_str = ''
    i = 0
    for st in assume_list:
        in_str += 'fof(a_a_'+str(i)+',axiom,'+st+').\n'
        i += 1
    for st in goal_list:
        in_str += 'fof(c_c_'+str(i)+',conjecture,'+st+').\n'
        i += 1
    out_str = run_program(['eprover', '--proof-object', '-'], in_str)
    proof = out_str.find("Proof found!")
    satis = out_str.find("CounterSatisfiable")
    # print(out_str)
    if proof != -1 or satis != -1:
        lst = out_str.split('\n')
        lst = [s[4:-2] for s in lst if s != "" and s[0] != "#"]
        #for s in lst: print(s)
        lst = [[int(re.search("[ac]_._(\d+)", s).group(1)),
                re.search(",\s[a-z_]+,\s(.*),\s[fi]", s).group(1),
                [int(x) for x in re.findall("[ac]_._(\d+)", s)[1:]]] for s in lst]
        for x in lst:  # remove outside universal quantifier
            ind = x[1].find(":")
            if x[1][0] == "!" and ind != -1:
                x[1] = x[1][ind+1:]
            if x[0] == x[2][0]:  # axioms have empty reasons
                x[2] = []
        for x in reversed(lst):
            if x[2] == []:
                x[2] = ['conjecture']
                break
        if proof != -1:
            print("Proof found!")
        if satis != -1:
            print("Saturated: counterexample exists!")
        return Proof(lst, 'TPTP')
    print('No conclusion (timeout)')
    return 'No conclusion (timeout)'
