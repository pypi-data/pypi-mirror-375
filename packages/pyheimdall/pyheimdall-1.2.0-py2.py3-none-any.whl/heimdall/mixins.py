# -*- coding: utf-8 -*-
from heimdall.util import (
    get_language, get_nodes, get_node,
    create_nodes, create_node,
    )

"""
Provides mixins for custom element classes.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""


class Documentable(object):

    @property
    def name(self):
        return self._icanhaz_get_dict('name')

    @name.setter
    def name(self, value):
        self._icanhaz_set_list('name', value)

    @name.deleter
    def name(self):
        self._icanhaz_del('name')

    @property
    def description(self):
        return self._icanhaz_get_dict('description')

    @description.setter
    def description(self, value):
        self._icanhaz_set_list('description', value)

    @description.deleter
    def description(self):
        self._icanhaz_del('description')

    @property
    def uri(self):
        return self._icanhaz_get_list('uri')

    @uri.setter
    def uri(self, values):
        if ((values is not None)
           and (type(values) is not list)
           and (type(values) is not str)):
            bad = str(type(values))
            raise TypeError(f"Argument must be list or str, got '{bad}'")
        self._icanhaz_set_list('uri', values)

    @uri.deleter
    def uri(self):
        self._icanhaz_del('uri')

    def _icanhaz_get_dict(self, tag):
        values = dict()
        for node in get_nodes(self, tag):
            lang = get_language(node)
            alternatives = values.get(lang, list())
            alternatives.append(node.text)
            values[lang] = alternatives
        return values

    def _icanhaz_get_list(self, tag):
        values = list()
        for node in get_nodes(self, 'uri'):
            values.append(node.text)
        return values

    def _icanhaz_set_list(self, tag, values):
        delattr(self, tag)
        create_nodes(self, tag, values)

    def _icanhaz_del(self, tag):
        for node in get_nodes(self, tag):
            self.remove(node)


class Typable(object):

    @property
    def type(self):
        node = get_node(self, 'type')
        return node.text if node is not None else None

    @type.setter
    def type(self, value):
        delattr(self, 'type')
        if value is not None:
            create_node(self, 'type', value)

    @type.deleter
    def type(self):
        node = get_node(self, 'type')
        if node is not None:
            self.remove(node)


class Repeatable(object):

    @property
    def min(self):
        return int(self.get('min', 0))

    @min.setter
    def min(self, value):
        if value is None:
            delattr(self, 'min')
            return
        # NOTE: min < 0 or min > max make no sense
        mn = max(int(value), 0)
        if self.max is None:
            self.set('min', str(mn))
        else:
            self.set('min', str(min(mn, self.max)))

    @min.deleter
    def min(self):
        self.attrib.pop('min', 0)

    @property
    def max(self):
        mx = self.get('max')
        return mx if mx is None else int(mx)

    @max.setter
    def max(self, value):
        if value is None:
            delattr(self, 'max')
            return
        # NOTE: max < 1 or max < min make no sense
        self.set('max', str(max(int(value), 1, self.min)))

    @max.deleter
    def max(self):
        self.attrib.pop('max', None)


class Node(object):

    parent = None

    @property
    def children(self):
        return list(self)
        # NOTE: for ALL children, and not just direct ones:
        # return [e for e in self.iter() if e is not self]

    def append(self, child):
        super().append(child)
        try:
            child.parent = self
        except AttributeError:
            pass  # `child` doesn't have this mixin

    def remove(self, child):
        try:
            child.parent = None
        except AttributeError:
            pass  # `child` doesn't have this mixin
        super().remove(child)


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'Documentable', 'Typable', 'Repeatable',
    'Node',
    '__copyright__', '__license__',
    ]
