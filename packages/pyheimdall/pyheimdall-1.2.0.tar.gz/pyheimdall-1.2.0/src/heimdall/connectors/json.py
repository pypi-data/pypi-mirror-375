# -*- coding: utf-8 -*-
import heimdall
from heimdall.util import get_node, get_nodes, get_language
from ..decorators import get_database, create_database
from json import load, loads, dump
from urllib.parse import urlparse
from urllib.request import urlopen
from xml.etree.ElementTree import Element

"""
Provides connectors to HERA-formatted JSON files.

This module defines input and output connectors to databases composed in full or in part of JSON files following the HERA schema.

* :py:class:`heimdall.connectors.json.getDatabase` is the input connector
* :py:class:`heimdall.connectors.json.createDatabase` is the output connector

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501


@get_database('hera:json')
def getDatabase(**options):
    r"""Imports a database from a HERA JSON file

    :param \**options: Keyword arguments, see below.
    :Keyword arguments:
        * **url** (:py:class:`str`) -- Local ou remote path of the JSON file to import
        * **format** (:py:class:`str`, optional) Always ``hera:json``
        * **encoding** (:py:class:`str`, optional, default: ``utf-8``) -- ``url`` file encoding
    :return: HERA element tree
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    Usage example: ::

      >>> import heimdall
      >>> tree = heimdall.getDatabase(format='hera:json', url='some/input.json')
      >>> # ... do stuff ...

    .. CAUTION::
       For future compability, this function shouldn't be directly called; as shown in the usage example above, it should only be used through :py:class:`heimdall.getDatabase`.
    """  # nopep8: E501
    url = options['url']
    encoding = options.get('encoding', 'utf-8')
    if not is_url(url):
        with open(url, 'r') as f:
            data = load(f)
    else:
        with urlopen(url) as response:
            data = loads(response.read().decode(encoding))
    return _create_tree(data)


def is_url(path):
    schemes = ('http', 'https', )
    return urlparse(path).scheme in schemes


def _create_tree(data):
    root = heimdall.util.tree.create_empty_tree()

    # create Properties if any
    properties = data.get('properties', None)
    if properties is not None:
        elements = root.get_container('properties')
        for o in properties:
            heimdall.createProperty(root, **o)

    # create Entities if any
    entities = data.get('entities', None)
    if entities is not None:
        elements = root.get_container('entities')
        for o in entities:
            e = heimdall.createEntity(root, **o)
            attributes = o.get('attributes', list())
            for c in attributes:
                heimdall.createAttribute(e, **c)

    # create Items if any
    items = data.get('items', None)
    if items is not None:
        elements = root.get_container('items')
        for o in items:
            metadata = o.pop('metadata', list())
            e = heimdall.createItem(root, **o)
            for m in metadata:
                value = m.pop('value', None)
                heimdall.createMetadata(e, value, **m)

    return root


@create_database('hera:json')
def createDatabase(tree, url, **options):
    r"""Serializes a HERA elements tree into a JSON file

    :param tree: HERA elements tree
    :param url: Path of the JSON file to create

    .. ERROR::
       This feature is not implemented yet.
       This can be either due to lack of resources, lack of demand, because it
       wouldn't be easily maintenable, or any combination of these factors.

       Interested readers can submit a request to further this topic.
       See the ``CONTRIBUTING`` file at the root of the repository for details.
    """
    data = _tree2object(tree)
    # write data to file
    indent = options.get('indent', 2)
    protek = options.get('ensure_ascii', False)
    with open(url, 'w', encoding='utf-8') as f:
        dump(data, f, indent=indent, ensure_ascii=protek)


def _tree2object(tree):
    data = dict()
    # convert properties to json-ready objects, add them to data
    elements = heimdall.getProperties(tree)
    if len(elements) > 0:
        data['properties'] = list()
    for element in elements:
        data['properties'].append(_property2object(element))
    # convert entities to json-ready objects, add them to data
    elements = heimdall.getEntities(tree)
    if len(elements) > 0:
        data['entities'] = list()
    for element in elements:
        data['entities'].append(_entity2object(element))
    # convert items to json-ready objects, add them to data
    elements = heimdall.getItems(tree)
    if len(elements) > 0:
        data['items'] = list()
    for element in elements:
        data['items'].append(_item2object(element))

    return data


def _property2object(p):
    return _xml2object(p)


def _entity2object(e):
    data = _xml2object(e)
    elements = heimdall.getAttributes(e)
    if len(elements) > 0:
        data['attributes'] = list()
    for element in elements:
        data['attributes'].append(_attribute2object(element))
    return data


def _attribute2object(a):
    data = _xml2object(a)
    data['pid'] = a.get('pid')
    data['min'] = int(a.get('min', 0))
    _param2int(a, data, 'max', None)
    return data


def _xml2object(x):
    data = dict()
    value = x.get('id', None)
    if value is not None:
        data['id'] = value
    # child --> unique value
    for tag in ['type', ]:
        try:
            array_of_one = [c.text for c in x.children if c.tag == tag]
            assert len(array_of_one) < 2
            if len(array_of_one) > 0 and array_of_one[0] is not None:
                data[tag] = array_of_one[0]
        except AttributeError:
            pass  # no type
    # child --> localized object
    for tag in ['name', 'description', ]:
        obj = _nodes2object(get_nodes(x, tag))
        if obj is not None:
            data[tag] = obj
    # child --> repeatable value
    for tag in ['uri', ]:
        array = _nodes2array(get_nodes(x, tag))
        if len(array) > 0:
            data[tag] = array
    return data


def _item2object(i):
    data = dict()
    for key in ['eid', ]:
        _param2text(i, data, key)
    elements = heimdall.getMetadata(i)
    if len(elements) > 0:
        data['metadata'] = list()
    for element in elements:
        data['metadata'].append(_metadata2object(element))
    return data


def _metadata2object(m):
    data = dict()
    for key in ['pid', 'aid', ]:
        _param2text(m, data, key)
    value = get_language(m)
    if value is not None:
        data['language'] = value
    value = _node2text(m)
    if value is not None:
        data['value'] = value
    return data


def _param2text(x, data, key, default=None):
    value = x.get(key, default)
    if value is not None:
        data[key] = value


def _param2int(x, data, key, default=None):
    value = x.get(key, default)
    if value is not None:
        data[key] = int(value)


def _node2text(node):
    return node.text


def _nodes2object(nodes):
    data = dict()
    for node in nodes:
        language = get_language(node)
        if language is not None:
            data[language] = node.text
        else:
            # emergency exit:
            # if there is even only 1 node with no language,
            # we'll return this one only
            return node.text
    if len(data) < 1:
        return None
    return data


def _nodes2array(nodes):
    data = list()
    for node in nodes:
        if node.text is not None:
            data.append(node.text)
    return data
