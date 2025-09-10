# -*- coding: utf-8 -*-

"""
Provides utility functions around HERA elements tree refactoring or cleanup.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""
from xml.etree.ElementTree import Element, QName


def get_nodes(tree, tag, filter=None, direct=True):
    """Retrieves specific elements in a HERA element tree.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param tag: (:py:class:`str`) -- Tag of elements to search for
    :param filter: (:py:class:`function`, optional) -- Filtering function
    :param direct: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, retrieves ``tree``'s direct children only; if ``False``, perform a deep search
    :return: Found elements
    :rtype: :py:class:`list` of :py:class:`xml.etree.ElementTree.Element`

    This function returns a :py:class:`list` of all elements from ``tree`` of tag ``tag`` and for which ``filter`` returns ``True``. The returned :py:class:`list` is empty if there is no such element.

    :see also: | :py:class:`heimdall.util.get_node` can be used to search for no more than one element in ``tree``.
               | :py:class:`heimdall.getItems`, :py:class:`heimdall.getMetadata`, :py:class:`heimdall.getProperties`, :py:class:`heimdall.getEntities` and :py:class:`heimdall.getAttributes` are dedicated retrieval functions to search for elements in a HERA database, and should be used whenever possible for future compatibility.
    """  # nopep8: E501
    if tree is None:
        return list()
    if direct:
        nodes = tree.findall(f'./{tag}')
    else:
        nodes = tree.findall(f'.//{tag}')
    if filter:
        return [node for node in nodes if filter(node)]
    return nodes


def get_node(tree, tag, filter=None, direct=True):
    """Retrieves a specific element in a HERA element tree.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param tag: (:py:class:`str`) -- Tag of elements to search for
    :param filter: (:py:class:`function`, optional) -- Filtering function
    :param direct: (:py:class:`bool`, optional, default: ``True``) -- If ``True``, retrieves ``tree``'s direct children only; if ``False``, perform a deep search
    :return: Found element
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    This function returns a single element from ``tree`` as defined by ``tag`` and ``filter``, or ``None`` if there is no element in ``tree`` corresponing to ``tag`` and ``filter``.
    It works exactly like :py:class:`heimdall.util.get_nodes`, but raises an ``IndexError`` if it could return more than one result.

    :see also: | :py:class:`heimdall.util.get_nodes` can be used to retrieve multiple elements in ``tree``.
               | :py:class:`heimdall.util.get_root` can retrieve ``tree``'s root element.
               | :py:class:`heimdall.getItem`, :py:class:`heimdall.getProperty`, :py:class:`heimdall.getEntity` and :py:class:`heimdall.getAttribute` are dedicated retrieval functions to search for a specific element in a HERA database, and should be used whenever possible for future compatibility.
    """  # nopep8: E501
    nodes = get_nodes(tree, tag, filter, direct)
    if len(nodes) == 0:
        return None
    if len(nodes) == 1:
        return nodes[0]
    raise IndexError(f"Too many {tag} elements ({len(nodes)})")


def get_root(tree):
    """Retrieves a HERA element tree root.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :return: `tree`
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    :see also: :py:class:`heimdall.util.get_node` can be used to search for any element in ``tree``.
    """  # nopep8: E501
    return tree


def get_language(node):
    """Retrieves the language of a node.

    :param node: (:py:class:`xml.etree.ElementTree.Element`) -- HERA element
    :return: ``node`` language
    :rtype: :py:class:`str`

    This function returns ``node``'s language, if it has any.
    The returned language `should be a language code <https://www.w3.org/International/questions/qa-when-xmllang.en.html>`_, but it will be any :py:class:`str` that was set in ``node``'s ``xml:lang`` attribute.

      >>> import heimdall
      >>> # ...
      >>> metadata = heimdall.getMetadata(item, ...)
      >>> language_code = heimdall.util.get_language(metadata)
      >>> # if metadata has: xml:lang='en_US',
      >>> #   then language_code would be "en_US".
      >>> # if metadata has: xml:lang='lolspeak',
      >>> #   then language_code would be "lolspeak".
      >>> # if metadata didn't have any `xml:lang` set,
      >>> #   then language_code would be `None`.

    :see also: :py:class:`heimdall.util.set_language` to set ``node``'s language.
    """  # nopep8: E501
    qname = QName('http://www.w3.org/XML/1998/namespace', 'lang')
    return node.get(qname)


def set_language(node, language):
    """Sets the language of a node.

    :param node: (:py:class:`xml.etree.ElementTree.Element`) -- HERA element
    :param language: (:py:class:`str`) -- Language code (`see documentation <https://www.w3.org/International/questions/qa-when-xmllang.en.html>`_
    :return: None
    :rtype: :py:class:`NoneType`

    This function set ``node``'s ``xml:lang`` attribute to value ``language``.

      >>> import heimdall
      >>> # ...
      >>> metadata = heimdall.getMetadata(item, ...)
      >>> heimdall.util.set_language(metadata, 'fr')
      >>> # now metadata has: xml:lang='fr'.
      >>> heimdall.util.set_language(metadata, None)
      >>> # now metadata has no more xml:lang set.

    :see also: :py:class:`heimdall.util.get_language` to retrieve ``node``'s language.
    """  # nopep8: E501
    qname = QName('http://www.w3.org/XML/1998/namespace', 'lang')
    return node.set(qname, language)


def create_empty_tree():
    r"""Creates an empty HERA database

    :return: HERA element tree
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    Usage example: ::
      >>> import heimdall
      >>> tree = heimdall.util.create_empty_tree()
      >>> # ... do stuff ...
    """
    from xml.etree.ElementTree import Element
    from heimdall.elements import Root
    root = Root()
    root.append(Element('properties'))
    root.append(Element('entities'))
    root.append(Element('items'))
    return root


def create_nodes(parent, tag, text):
    r"""Creates a child, or children, for a node.

    :param parent: (:py:class:`xml.etree.ElementTree.Element`) -- HERA element
    :param tag: (:py:class:`str`) -- Created child tag, or tag common to all created children
    :param tag: (:py:class:`str`\ \|\ :py:class:`dict`) -- See description
    :return: Children created
    :rtype: :py:class:`list` of :py:class:`xml.etree.ElementTree.Element`

    This function can be used to append a single child to a ``parent`` node: ::

      >>> import heimdall
      >>> # ...
      >>> entity = heimdall.getEntity(tree, ...)
      >>> heimdall.util.create_nodes(entity, 'description', "blah blah blah")

    This function can be used to append in one go multiple localized nodes to ``parent``: ::

      >>> import heimdall
      >>> # ...
      >>> entity = heimdall.getEntity(tree, ...)
      >>> heimdall.util.create_nodes(entity, 'description', {
      >>>     'de': "blabla",
      >>>     'en': "blah blah blah",
      >>>     'fr': "bla-bla",
      >>>     })

    :see also: :py:class:`heimdall.util.create_node` if you don't do internationalization.
    """  # nopep8: E501
    nodes = list()

    def _create(_parent, _tag, _text):
        _node = create_node(_parent, _tag, _text)
        nodes.append(_node)
        return _node

    if type(text) is str or type(text) is type(None):
        _create(parent, tag, text)
    elif type(text) is dict:
        for language_key, value in text.items():
            if type(value) is str or type(value) is type(None):
                node = _create(parent, tag, value)
                set_language(node, language_key)
            else:
                for v in value:
                    node = _create(parent, tag, v)
                    set_language(node, language_key)
    else:  # type(text) is list
        for value in text:
            _create(parent, tag, value)
    return nodes


def create_node(parent, tag, text=None):
    """Creates a child for a node.

    :param parent: (:py:class:`xml.etree.ElementTree.Element`) -- HERA element
    :param tag: (:py:class:`str`) -- Created child tag
    :param tag: (:py:class:`str`) -- Created child text
    :return: Child
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    This function appends a single child to a ``parent`` node: ::

      >>> import heimdall
      >>> # ...
      >>> entity = heimdall.getEntity(tree, ...)
      >>> heimdall.util.create_nodes(entity, 'description', "blah blah blah")

    :see also: :py:class:`heimdall.util.create_nodes` can be used to append in one go multiple localized nodes to ``parent``.
    """  # nopep8: E501
    if type(text) is not str and type(text) is not type(None):
        bad = str(type(text).__name__)
        raise TypeError(f"Argument 'text' must be str, got '{bad}'")

    node = Element(tag)
    parent.append(node)
    if text is not None:
        node.text = text
    return node


def get_container(tree, tag):
    nodes = tree.findall(f'.//{tag}')
    if len(nodes) == 0:
        return None
    assert len(nodes) == 1
    return nodes[0]


def create_container(tree, tag):
    container = get_container(tree, tag)
    if container is None:
        container = Element(tag)
        tree.append(container)
    return container


def update_node_value(node, key, value):
    if value is not None:
        node.set(key, str(value))
    else:  # remove value
        node.attrib.pop(key, None)


def maybe_update_node_values(node, keys, **kwargs):
    for key in keys:
        try:
            value = kwargs[key]
            update_node_value(node, key, value)
        except KeyError:
            pass  # nothing to change


def update_node_children(node, key, value):
    children = get_nodes(node, key)
    if len(children) == 0:
        create_nodes(node, key, value)
    for child in children:
        if value is not None:
            child.text = str(value)
        else:  # remove child node
            node.remove(child)


def maybe_update_node_children(node, keys, **kwargs):
    for key in keys:
        try:
            value = kwargs[key]
            update_node_children(node, key, value)
        except KeyError:
            pass  # nothing to change


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'get_node', 'get_nodes', 'get_root',
    'get_language', 'set_language',
    'create_empty_tree',
    'create_node', 'create_nodes',
    '__copyright__', '__license__',
    ]
