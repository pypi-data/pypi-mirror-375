# -*- coding: utf-8 -*-

"""
Provides CRUD operations to search for or
edit attributes in a HERA entity.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""

from .util.tree import (
        get_node as _get_node,
        get_nodes as _get_nodes,
        get_root as _get_root,
        create_node as _create_node,
        create_nodes as _create_nodes,
        maybe_update_node_values as _maybe_update_values,
        maybe_update_node_children as _maybe_update_children,
    )
from .elements import Attribute


def getAttribute(entity, filter):
    """Retrieves a single attribute from an entity.

    :param entity: (:py:class:`heimdall.elements.Entity`) -- HERA entity
    :param filter: (:py:class:`function`, optional) -- Filtering function
    :return: Attribute from ``entity``
    :rtype: :py:class:`heimdall.elements.Attribute`

    This function works exactly like :py:class:`heimdall.getAttributes`, but raises an ``IndexError`` if ``filter`` returns more than one result.
    """  # nopep8: E501
    return _get_node(entity, 'attribute', filter)


def getAttributes(entity, filter=None):
    """Retrieves attributes from an entity.

    :param entity: (:py:class:`heimdall.elements.Entity`) -- HERA entity
    :param filter: (:py:class:`function`, optional) -- Filtering function
    :return: Attributes subset from ``entity``
    :rtype: :py:class:`list` of :py:class:`heimdall.elements.Attribute`

    :Usage examples:

    This function can be used to retrieve all attributes of an entity: ::

      >>> import heimdall
      >>> ...  # create or load HERA tree
      >>> entity = heimdall.getEntity(tree, ...)  # retrieve an entity
      >>> attributes = heimdall.getAttributes(entity)  # retrieve all attributes

    To retrieve only *some* attributes, you can use a filter.
    A filter is a function which takes only one attribute as a parameter, and returns either ``True`` (we want this attribute to be part of the list returned by ``getAttributes``) or ``False`` (we don't want it). ::

      >>> import heimdall
      >>> ...  # create or load HERA tree
      >>> entity = heimdall.getEntity(tree, ...)  # retrieve an entity
      >>> def by_pid(attribute):  # create filtering function
      >>>     return attribute.get('pid') == 'dc:title'
      >>> # retrieve only attributes equivalent to a title
      >>> names = heimdall.getAttributes(entity, by_pid)

    For simple filters, anonymous functions can of course be used: ::

      >>> import heimdall
      >>> ...  # create or load HERA tree
      >>> entity = heimdall.getEntity(tree, ...)  # retrieve an entity
      >>> # retrieve only attributes equivalent to an identifier
      >>> ids = heimdall.getAttributes(entity, lambda a: a.get('pid') == 'id')
    """  # nopep8: E501
    return _get_nodes(entity, 'attribute', filter)


def createAttribute(entity, pid, **kwargs):
    r"""Adds a single attribute to an entity.

    :param entity: (:py:class:`heimdall.elements.Entity`) -- HERA entity
    :param pid: (:py:class:`str`) -- Linked property ID
    :param \**kwargs: (:py:class:`dict`, optional) -- Keyword arguments, see below.
    :Keyword arguments:
        * **id** (:py:class:`str`, optional) -- Attribute id
        * **min** (:py:class:`int`, optional, default: ``0``) -- Minimum occurences in an item: ``1`` or more means it is mandatory
        * **max** (:py:class:`int`, optional) -- Maximum occurences in an item: ``1`` means it is not repeatable, more (or no value) means it is; ``0`` or ``<min`` is undefined behaviour
        * **type** (:py:class:`str`, optional) -- Type override; no value means the linked property ``type`` will be used
        * **name** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Name override; no value means the linked property ``name`` will be used
        * **description** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Description override; no value means the linked property ``description`` will be used
        * **uri** (:py:class:`list` of :py:class:`str`, optional) -- URI list override; no value means the linked property ``uri`` will be used, any value adds to the property ``uri``
    :return: Attribute that was just created
    :rtype: :py:class:`heimdall.elements.Attribute`

    This function can be used to add a new attribute to an existing entity.
    Attributes created by ``createAttribute`` will always be added to the
    entity ``entity``, with no consistency check.
    For example, ``createAttribute`` does not verify that ``pid`` is a valid
    property identifier in the database ``entity`` comes from.

    :Usage examples:

    In its simplest usage, ``createAttribute`` simply creates
    a new ``<attribute pid='xxx'/>`` element: ::

      >>> import heimdall
      >>> ...
      >>> entity = heimdall.getEntity(...)
      >>> heimdall.createAttribute(entity, pid='xxx')  # create a new attribute
      >>> # the following child is now added to entity attributes list:
      >>> # <attribute pid='xxx' />

    Additional supported parameters are ``type``, ``name``, ``description``,
    and ``uri``.
    Each of these parameters creates appropriate children for the attribute.
    Here is an example: ::

      >>> import heimdall
      >>> ...
      >>> heimdall.createAttribute(entity,
      >>>     pid='dc:title', name='Label',
      >>>     uri=[
      >>>         'http://purl.org/dc/terms/title',
      >>>         'http://purl.org/dc/terms/alternative',
      >>>         'http://nakala.fr/terms#title'
      >>>     ])
      >>> # the following attribute is now added to the entity:
      >>> # <attribute pid='dc:title'>
      >>> #     <type>text</type>
      >>> #     <name>Label</name>
      >>> #     <uri>http://purl.org/dc/terms/title</uri>
      >>> #     <uri>http://purl.org/dc/terms/alternative</uri>
      >>> #     <uri>http://nakala.fr/terms#title</uri>
      >>> # </attribute>

    Please note that ``name`` and ``description`` can be localized, if they are
    of type :py:class:`dict` instead of :py:class:`str` (:py:class:`dict` keys are language codes).
    The following example shows attribute localization: ::

      >>> import heimdall
      >>> ...  # create HERA element tree
      >>> heimdall.createAttribute(entity,
      >>>      pid='dc:title',
      >>>      max='1',
      >>>      name={
      >>>          'de': "Name",
      >>>          'en': "Name",
      >>>          'fr': "Nom",
      >>>      },
      >>>      description={
      >>>          'en': "Human-readable name",
      >>>          'fr': "Nom usuel",
      >>>      })
      >>> # the following element is now added to the corresponding ``<entity/>`` element:
      >>> # <attribute pid='dc:title' min='0' max='1'>
      >>> #     <type>text</type>
      >>> #     <name xml:lang='de'>Name</name>
      >>> #     <name xml:lang='en'>Name</name>
      >>> #     <name xml:lang='fr'>Nom</name>
      >>> #     <description xml:lang='en'>Human-readable name</description>
      >>> #     <description xml:lang='fr'>Nom usuel</description>
      >>> # </attribute>
    """  # nopep8: E501
    param = kwargs.get('id', None)
    if param is not None:
        # Check attribute unique id (aid) does not exist
        if getAttribute(entity, lambda a: a.get('id') == param) is not None:
            raise ValueError(f"Attribute id '{param}' already exists")
        param = str(param)
    node = Attribute(pid=pid)
    if param is not None:
        node.set('id', param)
    param = kwargs.get('min', 0)
    node.min = param
    param = kwargs.get('max', None)
    node.max = param

    param = kwargs.get('type', None)
    if param is not None:
        _create_node(node, 'type', param)
    param = kwargs.get('name', None)
    if param is not None:
        node.name = param
    param = kwargs.get('description', None)
    if param is not None:
        node.description = param
    param = kwargs.get('uri', list())
    if type(param) is not list:
        raise TypeError(f"'uri' expected:'list', got:'{type(param).__name__}'")
    node.uri = param

    entity.append(node)
    return node


def replaceAttribute(attribute, **kwargs):
    """Replaces an existing attribute.

    .. ERROR::
       This feature is not implemented yet.
       This can be either due to lack of resources, lack of demand, because it wouldn't be easily maintenable, or any combination of these factors.

       Interested readers can submit a request to further this topic.
       See the ``CONTRIBUTING.rst`` file at the root of the repository for details.
    """  # nopep8: E501
    raise ValueError("TODO: Not Implemented")  # pragma: no cover


def updateAttribute(attribute, **kwargs):
    r"""Updates a single attribute.

    :param attribute: (:py:class:`heimdall.elements.Attribute`) -- HERA attribute
    :param \**kwargs: (:py:class:`dict`, optional) -- Keyword arguments, see below.
    :Keyword arguments:
        * **id** (:py:class:`str`, optional) -- Attribute id
        * **pid** (:py:class:`str`, optional) -- Property id
        * **min** (:py:class:`int`, optional, default: ``0``) -- Minimum occurences in an item: ``1`` or more means it is mandatory
        * **max** (:py:class:`int`, optional) -- Maximum occurences in an item: ``1`` means it is not repeatable, more (or no value) means it is; ``0`` or ``<min`` is undefined behaviour
        * **type** (:py:class:`str`, optional) -- Type override; no value means the linked property ``type`` will be used
        * **name** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Name override; no value means the linked property ``name`` will be used
        * **description** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Description override; no value means the linked property ``description`` will be used
        * **uri** (:py:class:`list` of :py:class:`str`, optional) -- URI list override; no value means the linked property ``uri`` will be used, any value adds to the property ``uri``
    :return: Attribute that was just updated
    :rtype: :py:class:`heimdall.elements.Attribute`

    This function can be used to update an existing attribute.
    Like ``createAttribute``, it makes with no consistency check.
    For example, ``createAttribute`` does not verify that ``pid`` is a valid property identifier in the database ``attribute`` comes from.

    :Usage examples:

    Any or all of ``updateAttribute`` parameters can be used to update ``attribute``: ::

      >>> import heimdall
      >>> # ...
      >>> attribute = heimdall.getAttribute(entity, ...)
      >>> heimdall.updateAttribute(attribute, name='Label', min=1)

    Please note that ``name`` and ``description`` can be localized, if they are of type :py:class:`dict` instead of :py:class:`str` (:py:class:`dict` keys are language codes).
    The following example shows attribute localization: ::

      >>> import heimdall
      >>> # ...
      >>> attribute = heimdall.getAttribute(entity, ...)
      >>> heimdall.updateAttribute(attribute,
      >>>      name={
      >>>          'de': "Name",
      >>>          'en': "Name",
      >>>          'fr': "Nom",
      >>>      },
      >>>      description={
      >>>          'en': "Human-readable name",
      >>>          'fr': "Nom usuel",
      >>>      })
    """  # nopep8: E501
    VALUES = ['id', 'pid', 'min', 'max', ]
    CHILDREN = ['type', 'name', 'description', 'uri', ]
    _maybe_update_values(attribute, VALUES, **kwargs)
    _maybe_update_children(attribute, CHILDREN, **kwargs)
    return attribute


def deleteAttribute(entity, filter):
    """Deletes a single Attribute from an entity.

    :param entity: (:py:class:`heimdall.elements.Entity`) -- HERA entity
    :param filter: (:py:class:`function`) -- Filtering function
    :return: None
    :rtype: :py:class:`NoneType`

    This function can be used to remove attributes from an entity.
    It performs the attribute deletion "in place" ; in other words, parameter ``tree`` is directly modified, and this function returns nothing.

    If ``filter`` returns no result, this function does nothing, and does not raise any error.

    This function doesn't delete any metadata referencing the ``pid`` of the deleted attribute.

    :Usage example: ::

      >>> import heimdall
      >>> ...  # create config, load HERA tree
      >>> # delete an attribute of a specific entity
      >>> e = heimdall.getEntity(tree, lambda e : e.get('id') == 'person')
      >>> heimdall.deleteAttribute(e, lambda a: a.get('pid') == 'religion')
    """  # nopep8: E501
    nodes = getAttributes(entity, filter)
    for node in nodes:
        entity.remove(node)


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'getAttribute', 'getAttributes',
    'createAttribute', 'deleteAttribute',
    'replaceAttribute', 'updateAttribute',
    '__copyright__', '__license__',
    ]
