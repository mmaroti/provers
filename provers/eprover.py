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
from .prover9 import Proof
import re

def E(assume_list, goal_list, prover_seconds=60, format='tptp', info=False, options=[]):
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
    if format=='p9':
        options = ['op(350,prefix,"~")', 'op(499,infix_left,["*","/","\","@"])',
               'op(599,infix_left,["+","^","v"])']+options  # add default options
        for st in options:
            in_str += st+'.\n'
        in_str += 'formulas(assumptions).\n'
        for st in assume_list:
            in_str += st+'.\n'
        in_str += 'end_of_list.\nformulas(goals).\n'
        for st in goal_list:
            in_str += st+'.\n'
        in_str += 'end_of_list.\n'
        if info:
            print("+++"+in_str)
        in_str = run_program(['ladr_to_tptp',''],in_str)
        if info:
            print("***"+in_str)
    else:
        i = 0
        for st in assume_list:
            in_str += 'fof(a_a_'+str(i)+',axiom,'+st+').\n'
            i += 1
        for st in goal_list:
            in_str += 'fof(c_c_'+str(i)+',conjecture,'+st+').\n'
            i += 1
        if info:
            print("***"+in_str)
    out_str = run_program(['eprover', '--proof-object', '-'], in_str)
    proof = out_str.find("Proof found!")
    satis = out_str.find("CounterSatisfiable")
    if info:
        print("&&&"+out_str)
    if proof != -1 or satis != -1:
        lst = out_str.split('\n')
        lst = [s[4:-2] for s in lst if s != "" and s[0] != "#"]
        if info:
            for s in lst: 
                print("***"+s)
        conjecture = [i for i in range(len(lst)) if lst[i].find(' conjecture')!=-1]
        lst = [[re.search("[ac]_._(\d+)|sos|goals", s).group(1),
                re.search(",\s[a-z_]+,\s(.+?),\s[fis]", s).group(1),
                [x for x in re.findall("[ac]_._(\d+)", s)[1:]]] for s in lst]
        for x in lst:
            x[0] = int(x[0]) if x[0]!=None else 0
            x[2] = [int(y) for y in x[2]]
            ind = x[1].find(":") # remove outside universal quantifier
            if x[1][0] == "!" and ind != -1:
                x[1] = x[1][ind+1:]
            x[1] = x[1].replace('tptp','t')
            x[1] = x[1].replace('esk','s')
            x[1] = x[1].replace('X','x')
            x[1] = x[1].replace('=',' = ')
            x[1] = x[1].replace('< = >',' <=> ')
            x[1] = x[1].replace(' = >',' => ')
            x[1] = x[1].replace('! =',' != ')
            x[1] = x[1].replace('|',' | ')
            x[1] = x[1].replace('&',' & ')
            x[1] = x[1].replace(':',': ')
            if x[2]!=[] and x[0] == x[2][0]: # axioms have empty reasons
                x[2] = []
        lst[conjecture[0]][2] = ['conjecture'] # mark conjecture
        if proof != -1:
            print("Proof found!")
        if satis != -1:
            print("Saturated: counterexample exists!")
        return Proof(lst, 'TPTP')
    print('No conclusion (timeout)')
    return 'No conclusion (timeout)'