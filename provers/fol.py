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

"""
This module contains classes to work with first order formulas.
"""


class Relation(object):
    def __init__(self, name, arity):
        assert arity >= 0
        self.name = name
        self.arity = arity

    def __call__(self, *arguments):
        return Predicate(self, arguments)

    def __repr__(self):
        return 'Relation("'+self.name+'",'+str(self.arity)+')'


class Function(object):
    def __init__(self, name, arity):
        assert arity >= 0
        self.name = name
        self.arity = arity

    def __call__(self, *arguments):
        return Composition(self, arguments)

    def __repr__(self):
        return 'Function("'+self.name+'",'+str(self.arity)+')'


class Term(object):
    def eq(self, other):
        return Equals(self, other)


class Variable(Term):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return '"'+self.name+'"'

class Composition(Term):
    def __init__(self, function, arguments):
        assert isinstance(function, Function)
        assert function.arity == len(arguments)
        self.function = function
        self.arguments = arguments


class Formula(object):
    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __invert__(self):
        return Not(self)


class Predicate(Formula):
    def __init__(self, relation, arguments):
        super().__init__()
        assert isinstance(relation, Relation)
        assert relation.arity == len(arguments)
        self.relation = relation
        self.arguments = arguments

    def __invert__(self):
        return Not(self)

    def __repr__(self):
        return str(self.relation)+'('+','.join([str(x) for x in self.arguments])+')'


class And(Formula):
    def __init__(self, first, second):
        super().__init__()
        assert isinstance(first, Formula)
        assert isinstance(second, Formula)
        self.first = first
        self.second = second

    def __invert__(self):
        return Not(self)

    def __repr__(self):
        return str(self.first)+' & '+str(self.second)


class Or(Formula):
    def __init__(self, first, second):
        super().__init__()
        assert isinstance(first, Formula)
        assert isinstance(second, Formula)
        self.first = first
        self.second = second

    def __invert__(self):
        return Not(self)

    def __repr__(self):
        return str(self.first)+' | '+str(self.second)


class Not(Formula):
    def __init__(self, other):
        super().__init__()
        assert isinstance(other, Formula)
        self.other = other

    def __invert__(self):
        return self.other

    def __repr__(self):
        return '~'+str(self.other)


class Equals(Formula):
    def __init__(self, first, second):
        super().__init__()
        assert isinstance(first, Term)
        assert isinstance(second, Term)
        self.first = first
        self.second = second

    def __invert__(self):
        return Not(self)

