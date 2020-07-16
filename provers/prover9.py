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


class Proof():
    def __init__(self, formula_list, syntax='Prover9'):
        """
        Stores a proof as a list of formulas.

        INPUT:
            syntax -- a string that indicates what syntax is used for the
                formulas that represent the proof, e.g. "Prover9".
            formula_list -- a list of lists. Each list entry is a list of the
                form [formula, line_number, [references_to_preceding_lines]].
                The references indicate which preceding lines are used in the
                derivation of the current line.
        """
        self.syntax = syntax
        self.proof = formula_list

    def __repr__(self):
        """
        Display a proof as a list of lines.
        """
        st = '\nProof(syntax=\"' + self.syntax + '\", formula_list=[\n'
        for l in self.proof[:-1]:
            st += str(l) + ',\n'
        return st + str(self.proof[-1]) + '])'


def opstr(m):  # convert 2-dim list to a compact string for display
    nr = len(m)
    if nr == 0:
        return "[]"
    nc = len(m[0])
    s = [[str(y).replace(' ', '') for y in x] for x in m]
    width = [max([len(s[x][y]) for x in range(nr)]) for y in range(nc)]
    s = [[" "*(width[y]-len(s[x][y]))+s[x][y] for y in range(nc)]
         for x in range(nr)]
    rows = ["["+",".join(x)+"]" for x in s]
    s = "[\n"+",\n".join(rows)+"]"
    return s


def oprelstr(oprel):  # convert a list of operations or relations to a string
    st = ''
    for x in oprel:
        if type(oprel[x]) == list and type(oprel[x][0]) == list:
            st += '\n"'+x+'":' + opstr(oprel[x]) + ', '
        else:
            st += '"'+x+'":' + str(oprel[x]) + ', '
    return st[:-2]


def op_var_pos_diag(op, s, c):
    if type(op[s]) == list:
        base = range(len(op[s]))
        if type(op[s][0]) == list:
            return [c+str(x)+" "+s+" "+c+str(y)+" = "+c+str(op[s][x][y])
                    for x in base for y in base]
        elif s == "'":
            return [c+str(x)+s+" = "+c+str(op[s][x]) for x in base]
        else:
            return [s+"("+c+str(x)+") = "+c+str(op[s][x]) for x in base]
    else:
        return [s+" = "+c+str(op[s])]


def rel_var_pos_diag(rel, s, c):
    if type(rel[s]) == list:
        base = range(len(rel[s]))
        if type(rel[s][0]) == list:
            if type(rel[s][0][0]) == list:  # if prefix ternary relation
                return [s+"("+c+str(x)+","+c+str(y)+","+c+str(z)+")"
                        for x in base for y in base for z in base if rel[s][x][y][z]]
            else:  # if infix binary relation
                return [c+str(x)+" "+s+" "+c+str(y)
                        for x in base for y in base if rel[s][x][y]]
        else:
            return [s+"("+c+str(x)+")" for x in base if rel[s][x]]
    else:
        return "not a relation"


def op_var_diag(op, s, c, n=0):
    if type(op[s]) == list:
        base = range(len(op[s]))
        if type(op[s][0]) == list:
            return [c+str(x+n)+" "+s+" "+c+str(y+n)+" = "+c+str(op[s][x][y]+n)
                    for x in base for y in base]
        elif s == "'":
            return [c+str(x+n)+s+" = "+c+str(op[s][x]+n) for x in base]
        else:
            return [s+"("+c+str(x+n)+") = "+c+str(op[s][x]+n) for x in base]
    else:
        return [s+" = "+c+str(op[s]+n)]


def rel_var_diag(rel, s, c, n=0):
    if type(rel[s]) == list:
        base = range(len(rel[s]))
        if type(rel[s][0]) == list:
            if type(rel[s][0][0]) == list:  # prefix ternary relation
                return [("" if rel[s][x][y][z] else "-")+s+"("+c+str(x+n) +
                        ","+c+str(y+n)+","+c+str(z+n)+")"
                        for x in base for y in base for z in base]
            elif s >= "A" and s <= "Z":  # prefix binary relation
                return [("" if rel[s][x][y] else "-")+s+"("+c+str(x+n) +
                        ","+c+str(y+n)+")" for x in base for y in base]
            else:  # infix binary relation
                return [("(" if rel[s][x][y] else "-(")+c+str(x+n)+" " +
                        s+" "+c+str(y+n)+")" for x in base for y in base]
        else:
            return [("" if rel[s][x] else "-")+s+"("+c+str(x+n)+")"
                    for x in base]
    else:
        return "not a relation"


def op_hom(A, B):  # return string of homomorphism equations
    st = ''
    for s in B.operations:
        if type(B.operations[s]) == list:
            if type(B.operations[s][0]) == list:
                st += " & h(x "+s+" y) = h(x) "+s+" h(y)"
            elif s == "'":
                st += " & h(x') = h(x)'"
            else:
                st += " & h("+s+"(x)) = "+s+"(h(x))"
        else:
            st += " & h("+str(B.operations[s] +
                              A.cardinality)+") = "+str(A.operations[s])
    return st


def aritystr(t): return ("(_,_)" if type(
    t[0]) == list else "(_)") if type(t) == list else ""


def op2li(t): return ([x for y in t for x in y] if type(
    t[0]) == list else t) if type(t) == list else [t]


class Model():
    def __init__(self, cardinality, index=None, operations={}, relations={},
                 **kwargs):
        """
        Construct a finite first-order model.

        INPUT:
            cardinality -- number of elements of the model's base set
            index -- a natural number giving the position of the model 
                in a list of models
            operations  -- a dictionary of operations on [0..cardinality-1].
                Entries are symbol:table pairs where symbol is a string 
                that denotes the operation symbol, e.g. '+', and table is
                an n-dimensional array with entries from [0..cardinality-1].
                n >= 0 is the arity of the operation (not explicitly coded 
                but can be computed from the table).
            relations -- a dictionary of relations on [0..cardinality-1].
                Entries are symbol:table pairs where symbol is a string 
                that denotes the relation symbol, e.g. '<', and table is
                an n-dimensional array with entries from [0,1] (coding 
                False/True). Alternatively the table can be an 
                (n-2)-dimensional array with entries that are dictionaries
                with keys [0..cardinality-1] and values subsets of [0..cardinality-1],
                given as ordered lists.
                n >= 0 is the arity of the relation (not explicitly coded 
                but can be computed from the table).
            other optional arguments --
                uc  -- a dictionary with keys [0..cardinality-1] and values 
                    an ordered list of upper covers. Used for posets.
                pos -- list of [x,y] coordinates for element positions
                labels -- list of n strings that give a label for each element
                is_... -- True/False properties are stored here
        """

        self.cardinality = cardinality
        self.index = index
        self.operations = operations
        self.relations = relations
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])

    def __repr__(self):
        """
        display a model
        """
        st = '\nModel(cardinality = '+str(self.cardinality) +\
             (', index = '+str(self.index) if self.index != None else '')
        if self.operations != {}:
            st += ',\noperations = {' + oprelstr(self.operations) + '}'
        if self.relations != {}:
            st += ',\nrelations = {' + oprelstr(self.relations) + '}'
        other = set(vars(self)) - \
            set(["cardinality", "index", "operations", "relations"])
        for attr in other:
            st += ',\n' + attr + ' = ' + str(getattr(self, attr))
        return st + ')'

    def positive_diagram(self, c):
        """
        Return the positive diagram of the algebra or structure
        """
        li = []
        for x in self.operations:
            li += op_var_pos_diag(self.operations, x, c)
        for x in self.relations:
            li += rel_var_pos_diag(self.relations, x, c)
        return li

    def diagram(self, c, s=0):
        """
        Return the diagram of the algebra or structure, prefix c, shift s
        """
        li = []
        for x in range(self.cardinality):
            for y in range(x+1, self.cardinality):
                li += ["-("+c+str(x+s)+"="+c+str(y+s)+")"]
        for x in self.operations:
            li += op_var_diag(self.operations, x, c, s)
        for x in self.relations:
            li += rel_var_diag(self.relations, x, c, s)
        return li

    def find_extensions(self, cls, cardinality, mace_time=60):
        """
        Find extensions of this model of given cardinality card in FOclass cls
        """
        n = self.cardinality
        ne = ['c'+str(x)+'!=c'+str(y) for x in range(n) for y in range(x+1, n)]
        return prover9(cls.axioms+ne+self.positive_diagram('c'), [],
                       mace_time, 0, cardinality)

    def inS(self, B, info=False):
        """
        check if self is a subalgebra of B, if so return sublist of B
        """
        if self.cardinality > B.cardinality:
            return False
        if info:
            print(self.diagram('a')+B.diagram(''))
        m = prover9(self.diagram('a')+B.diagram(''), [],
                    6000, 0, B.cardinality, [], True)
        if len(m) == 0:
            return False
        return [m[0].operations['a'+str(i)] for i in range(self.cardinality)]

    def inH(self, B, info=False):
        """
        check if self is a homomorphic image of B, if so return homomorphism
        """
        if self.cardinality > B.cardinality:
            return False
        formulas = self.diagram('')+B.diagram('', self.cardinality) +\
            ['A('+str(i)+')' for i in range(self.cardinality)] +\
            ['-B('+str(i)+')' for i in range(self.cardinality)] +\
            ['B('+str(i)+')' for i in range(self.cardinality, self.cardinality+B.cardinality)] +\
            ['-A('+str(i)+')' for i in range(self.cardinality, self.cardinality+B.cardinality)] +\
            ['B(x) & B(y) -> A(h(x)) & A(h(y))'+op_hom(self, B),
             'A(y) -> exists x (B(x) & h(x) = y)']
        if info:
            print(formulas)
        m = prover9(formulas, [], 6000, 0,
                    self.cardinality+B.cardinality, [], True)
        if len(m) == 0:
            return False
        return m[0].operations['h'][self.cardinality:]

    @staticmethod
    def mace4format(A):
        if A.is_lattice():
            A.get_join()
        st = "interpretation("+str(A.cardinality) + \
            ", [number = "+str(A.index)+", seconds = 0], [\n"
        st += ',\n'.join([" function("+s+aritystr(A.operations[s])+", " +
                          str(op2li(A.operations[s])).replace(" ", "")+")" for s in A.operations])
        if len(A.operations) > 0 and len(A.relations) > 0:
            st += ',\n'
        st += ',\n'.join([" relation("+s+aritystr(A.relations[s])+", " +
                          str(op2li(A.relations[s])).replace(" ", "")+")" for s in A.relations])
        return st+"])."


def isofilter(li):
    st = "\n".join([x.mace4format() for x in li])
    st = run_program(['isofilter'], st)
    st = run_program(['interpformat', 'portable'], st)
    l = eval(st.replace("\\", "\\\\"))
    models = []
    for m in l:
        models += [Model(m[0], m[1][0][9:-1], getops(m[2],'function'), getops(m[2], 'relation'))]
    return models


def getops(li, st):  # extract operations/relations from the Prover9 model
    return dict([op[1], op[3]] for op in li if op[0] == st)


def proofstep2list(st):  # convert a line of the Prover9 proof to a list
    li = st.split('.')
    ind = li[0].find(' ')
    return [eval(li[0][:ind])]+[li[0][ind+1:]]+[eval(li[-2])]


def prover9(assume_list, goal_list, mace_seconds=2, prover_seconds=60, cardinality=None,
            options=[], one=False, noniso=True, info=False, params=''): #later: hints_list=[], keep_list=[], delete_list=[]
    """
    Invoke Prover9/Mace4 with lists of formulas and some (limited) options

    INPUT:
        assume_list -- list of Prover9 formulas that assumptions
        goal_list -- list of Prover9 formulas that goals
        mace_seconds -- number of seconds to run Mace4
        prover_seconds -- number of seconds to run Prover9 (only runs if mace_seconds<5)
        cardinality -- if None, search for 1 counter model staring from cardinality 2
            if cardinality = n (>=2), search for all nonisomorphic models of
            cardinality n. If cardinality = [n] find all models of cardinality 2 to n
        options -- list of prover9 options (default [], i.e. none)
        one -- find only one model of given cardinality
        noniso -- if True, remove isomorphic copies
        info -- print input and output of prover9

    EXAMPLES:
        >>> p9(['x=x'], ['x=x']) # trivial proof

        >>> p9(['x=x'], ['x=y']) # trivial counterexample

        >>> Group = ['(x*y)*z = x*(y*z)', 'x*1 = x', "x*i(x) = 1"]
        >>> BooleanGroup = Group + ['x*x = 1']
        >>> p9(BooleanGroup, ['x*y = y*x']) # Boolean groups are abelian

        >>> p9(BooleanGroup, [], 3, 0, 50) # No model of cardinality 50
                                                # Boolean groups have cardinality 2^k
    """
    in_str = ''
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
        print(in_str)
    if mace_seconds != 0:
        mace_params = []
        if cardinality != None:
            st = str(cardinality)
            mace_params = ['-n', st, '-N', st] + \
                ([] if one else ['-m', '-1'])+['-S', '1']
        if info:
            print(mace_params)
        out_str = run_program(
            ['mace4', '-t', str(mace_seconds)]+mace_params, in_str)
        if info:
            print(out_str)
        ind = out_str.find("%%ERROR")
        if ind != -1:
            print(out_str[ind+2:])
            return
        if out_str.find('Exiting with failure') == -1:
            if cardinality != None and not one and noniso:  # find all models of size n
                out_str = run_program(['interpformat', 'standard'], out_str)
                if params=='':
                    params = '\" + * v ^ \' - ~ \\ / -> A B C D E F G H I J K P Q R S T U V W a b c d e f g h i j k p q r s t 0 1 <= -<\"'
                else:
                    params = '\" '+params+' \"'
                out_str = run_program(
                    ['isofilter', 'check', params, 'output', params], out_str)
                out_str = run_program(['interpformat', 'portable'], out_str)
            else:
                out_str = run_program(['interpformat', 'portable'], out_str)
            if out_str != '':
                #print(out_str)
                li = eval(out_str.replace("\\", "\\\\"))
            else:
                print("No models found (so far)")
                return
            models = []
            for m in li:
                models += [Model(m[0], len(models), getops(m[2],'function'), getops(m[2], 'relation'))]
            if cardinality != None and not one:
                print("Number of "+("nonisomorphic " if noniso else "") + "models of cardinality", cardinality,
                      " is ", len(models))
            return models
        elif cardinality != None and out_str.find('exit (exhausted)') != -1:
            if not one:
                print('No model of cardinality '+str(cardinality))
            return []
        elif mace_seconds >= 5:
            return "No models found after "+str(mace_seconds)+" seconds"

    out_str = run_program(['prover9', '-t', str(prover_seconds)], in_str)
    if info:
        print(out_str)
    ind = out_str.find("%%ERROR")
    if ind != -1:
        print(out_str[ind+2:])
        return
    if True:  # res==0 or res==1 or res==256:
        out_str = run_program(['prooftrans', 'expand', 'renumber', 'parents_only'], out_str)
        lst = []
        ind1 = out_str.find("PROOF ===")
        ind2 = out_str.find("end of proof ===")
        while ind1 != -1:
            lst.append([proofstep2list(x)
                        for x in out_str[ind1:ind2].split('\n')[10:-2]])
            ind1 = out_str.find("PROOF ===", ind2)
            ind2 = out_str.find("end of proof ===", ind2+1)
        return [Proof(li) for li in lst]
    print('No conclusion (timeout)')
    return 'No conclusion (timeout)'


def p9(assume_list, goal_list, mace_seconds=2, prover_seconds=60, cardinality=None, params='', info=False):
    if type(cardinality) == int or cardinality == None:
        return prover9(assume_list, goal_list, mace_seconds, prover_seconds, cardinality, params=params, info=info)
    else:
        algs = [[], [1]]+[[] for i in range(2, cardinality[0]+1)]
        for i in range(2, cardinality[0]+1):
            algs[i] = prover9(assume_list, goal_list, mace_seconds, prover_seconds, i, params=params, info=info)
        print("Fine spectrum: ", [len(x) for x in algs[1:]])
        return algs


import networkx as nx
from graphviz import Graph
from IPython.display import display_html
def hasse_diagram(op,rel,dual,unary=[]):
    A = range(len(op))
    G = nx.DiGraph()
    if rel:
        G.add_edges_from([(x,y) for x in A for y in A if (op[y][x] if dual else op[x][y]) and x!=y])
    else: 
        G.add_edges_from([(x,y) for x in A for y in A if op[x][y]==(y if dual else x) and x!=y])
    try:
        G = nx.algorithms.dag.transitive_reduction(G)
    except:
        pass
    P = Graph()
    P.attr('node', shape='circle', width='.15', height='.15', fixedsize='true', fontsize='10')
    for x in A: P.node(str(x), color='red' if unary[x] else 'black')
    P.edges([(str(x[0]),str(x[1])) for x in G.edges])
    return P

def m4diag(li,symbols="<= v", unaryRel=""):
    # use graphviz to display a mace4 structure as a diagram
    # symbols is a list of binary symbols that define a poset or graph
    # unaryRel is a unary relation symbol that is displayed by red nodes
    i = 0
    sy = symbols.split(" ")
    #print(sy)
    st = ""
    for x in li:
        i+=1
        st+=str(i)
        uR = x.relations[unaryRel] if unaryRel!="" else [0]*x.cardinality
        for s in sy:
            t = s[:-1] if s[-1]=='d' else s
            if t in x.operations.keys():
                st+=hasse_diagram(x.operations[t],False,s[-1]=='d',uR)._repr_svg_()+"&nbsp; &nbsp; &nbsp; "
            elif t in x.relations.keys():
                st+=hasse_diagram(x.relations[t], True, s[-1]=='d',uR)._repr_svg_()+"&nbsp; &nbsp; &nbsp; "
        st+=" &nbsp; "
    display_html(st,raw=True)

def p9latex(pf, latex=False):
    # print a proof in latex format (slightly more readable)
    from IPython.display import display, Math
    import re
    la = [str(li[0])+"\\quad "+re.sub(r"c(\d)",r"c_\1",li[1]).\
          replace(" * ","").replace("<=","\le ").replace("!=","\\ne ").\
          replace("\\ ","\\backslash ").replace(" <->","\iff").\
          replace(" ->","\\implies").replace("exists","\exists").\
          replace("# label(non_clause)","").replace("# label(goal)","\quad(goal)").\
          replace("&","\ \&\ ").replace("|","\quad\mbox{or}\quad").replace("$F","F")\
          +"\\quad "+str(li[2]) for li in pf[0].proof]
    if latex: return "$"+"$\n\n$".join(la)+"$"
    else:
        for st in la: display(Math(st))

def p9lean(pf):
    # print a proof in Lean syntax
    la = [str(li[0])+"     "+li[1].\
          replace("c1","x₁").replace("c2","y₂").replace("c3","z₃").\
          replace(" * ","⬝").replace("<=","≤").replace("!=","≠").\
          replace(" \\ ","﹨").replace("-(","¬(").replace("<->","↔").\
          replace(" / ","/").replace("->","→").replace("exists","∃").\
          replace("# label(non_clause)","").replace("# label(goal)","  (goal)").\
          replace("&","∧").replace("|","∨").replace("$F","F")\
          +"   "+str(li[2]) for li in pf[0].proof]
    return la #"\n".join(la)
