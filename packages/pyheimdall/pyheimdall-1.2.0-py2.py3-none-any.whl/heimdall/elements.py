# -*- coding: utf-8 -*-
from xml.etree.ElementTree import Element, QName
from heimdall.mixins import *


"""
Provides custom element classes.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""


class Root(Node, Element):
    """HERA element tree root
    """
    def __init__(self, **kwargs):
        xml_schema = 'http://www.w3.org/2001/XMLSchema-instance'
        xsd = 'https://gitlab.huma-num.fr/datasphere/hera/schema/schema.xsd'
        qname = QName(xml_schema, 'schemaLocation')
        kwargs[qname] = xsd  # NOTE: maybe we could NOT force this?
        super().__init__('hera', **kwargs)

    def get_container(self, tag):
        for c in self.children:
            if c.tag == tag:
                return c
        return None


class Item(Node, Element):
    """Item custom element
    """
    def __init__(self, **kwargs):
        super().__init__('item', **kwargs)

    @property
    def metadata(self):
        return [e for e in self.iter() if e is not self]


class Metadata(Node, Element):
    """Metadata custom element
    """
    def __init__(self, **kwargs):
        super().__init__('metadata', **kwargs)


class Property(Documentable, Typable, Node, Element):
    """Property custom element
    """
    def __init__(self, **kwargs):
        super().__init__('property', **kwargs)


class Entity(Documentable, Node, Element):
    """Entity custom element
    """
    def __init__(self, **kwargs):
        super().__init__('entity', **kwargs)

    @property
    def attributes(self):
        return [e for e in self.children if e.tag == 'attribute']

    def append(self, child):
        super().append(child)
        if type(child) is Attribute:
            child.entity = self


class Attribute(Documentable, Typable, Repeatable, Node, Element):
    """Attribute custom element
    """
    def __init__(self, **kwargs):
        super().__init__('attribute', **kwargs)


class Builder(object):

    TAGS = {
        'hera': Root,
        'item': Item,
        'metadata': Metadata,
        'property': Property,
        'entity': Entity,
        'attribute': Attribute,
        }
    root = None
    parent = None

    stack = list()

    @property
    def current(self):
        try:
            return self.stack[-1]
        except IndexError:
            return None

    def start(self, tag, attrib):
        """Called for each opening ``tag`` and their attributes ``attrib``
        """
        try:
            element = self.TAGS[tag](**attrib)
        except KeyError:
            element = Element(tag, **attrib)
        if self.parent is None:
            self.root = element
        else:
            self.parent.append(element)
        self.parent = element
        self.stack.append(element)

    def end(self, tag):
        """Called for each closing ``tag``
        """
        element = self.stack.pop()
        self.parent = self.current

    def data(self, data):
        """Called for each element ``data`` (ie. text)
        """
        if self.current.text is None:
            self.current.text = data
        else:
            self.current.text += data

    def close(self):
        """Called when all data has been parsed
        """
        return self.root


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'Builder',
    'Root',
    'Item', 'Metadata',
    'Property',
    'Entity', 'Attribute',

    '__copyright__', '__license__',
    ]
