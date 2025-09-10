# -*- coding: utf-8 -*-
import heimdall
from xml.etree import ElementTree as etree
from urllib.parse import urlparse
from urllib.request import urlopen
from ..decorators import get_database, create_database

"""
Provides connectors to HERA-formatted XML files.

This module defines input and output connectors to databases composed in full or in part of XML files following the HERA schema.

* :py:class:`heimdall.connectors.xml.getDatabase` is the input connector
* :py:class:`heimdall.connectors.xml.createDatabase` is the output connector

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501


@get_database(['hera:xml', ])
def getDatabase(**options):
    r"""Imports a database from a HERA XML file

    :param \**options: Keyword arguments, see below.
    :Keyword arguments:
        * **url** (:py:class:`str`) -- Local ou remote path of the XML file to import
        * **format** (:py:class:`str`, optional) Always ``hera:xml``
        * **encoding** (:py:class:`str`, optional, default: ``utf-8``) -- ``url`` file encoding
    :return: HERA element tree
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    Usage example: ::

      >>> import heimdall
      >>> tree = heimdall.getDatabase(format='hera:xml', url='some/input.xml')
      >>> # ... do stuff ...

    .. CAUTION::
       For future compability, this function shouldn't be directly called; as shown in the usage example above, it should only be used through :py:class:`heimdall.getDatabase`.
    """  # nopep8: E501
    url = options['url']
    encoding = options.get('encoding', 'utf-8')
    if is_url(url):
        with urlopen(url) as response:
            content = response.read().decode(encoding)
        # can raise urllib.error.HTTPError (HTTP Error 404: Not Found, ...)
    else:
        with open(url, 'r') as f:
            content = f.read()
        # can raise OSError (file not found, ...)
    target = heimdall.elements.Builder()
    parser = etree.XMLParser(target=target)
    return etree.fromstring(content, parser)


def is_url(path):
    schemes = ('http', 'https', 'file', )
    return urlparse(path).scheme in schemes


@create_database(['hera:xml', ])
def createDatabase(tree, url, pretty=True, **options):
    r"""Serializes a HERA elements tree into an XML file

    :param tree: (:py:class:`xml.etree.ElementTree.Element`) HERA elements tree
    :param url: (:py:class:`str`) Path of the XML file to create
    :param format: (:py:class:`str`) Always ``hera:xml``
    :return: None
    :rtype: :py:class:`NoneType`

    Usage example: ::
      >>> import heimdall
      >>> tree = heimdall.getDatabase(format='hera:xml', url='input.xml')
      >>> # ... do stuff ...
      >>> heimdall.createDatabase(tree, format='hera:xml', url='output.xml')
    """
    tree = etree.ElementTree(tree)
    etree.indent(tree, space='  ', level=0)
    with open(url, 'w') as f:
        tree.write(f, encoding='unicode')


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'getDatabase',
    'createDatabase',

    '__copyright__', '__license__',
    ]
