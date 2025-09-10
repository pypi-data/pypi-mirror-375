# -*- coding: utf-8 -*-

"""
Provides CRUD operations to search for or
edit properties in a HERA element tree.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""

from heimdall.util.tree import (
        get_node, get_nodes,
        get_container, create_container,
        maybe_update_node_values as _maybe_update_values,
        maybe_update_node_children as _maybe_update_children,
    )
from .elements import Property


def getProperty(tree, filter):
    """Retrieves a single property.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param filter: (:py:class:`function`) -- Filtering function
    :return: Property element
    :rtype: :py:class:`heimdall.elements.Property`

    This function returns a single property from ``tree`` as defined by ``filter``, or ``None`` if there is no property in ``tree`` corresponing to ``filter`` (or if ``tree`` has no property).
    It works exactly like :py:class:`heimdall.getProperties`, but raises an ``IndexError`` if ``filter`` returns more than one result.
    """  # nopep8: E501
    container = get_node(tree, 'properties')
    return get_node(container, 'property', filter)


def getProperties(tree, filter=None):
    """Retrieves a collection of properties.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param filter: (:py:class:`function`, optional) -- Filtering function
    :return: List of Property elements
    :rtype: :py:class:`list` of :py:class:`heimdall.elements.Property`

    :Usage examples:

    This function can be used to retrieve all properties in a database: ::

      >>> import heimdall
      >>> ...  # create config
      >>> tree = heimdall.getDatabase(config)  # load HERA tree
      >>> properties = heimdall.getProperties(tree)  # retrieve all properties

    To retrieve only *some* properties, you can use a filter.
    A filter is a function which takes only a property as a parameter, and returns either ``True`` (we want this property to be part of the list returned by ``getProperties``) or ``False`` (we don't want it). ::

      >>> import heimdall
      >>> ...  # create config, load HERA tree
      >>> def by_pid(property):  # create filtering function
      >>>     return property.get('id') == 'dc:title'
      >>> # retrieve only a specific property by its id
      >>> properties = heimdall.getProperties(tree, by_pid)

    For simple filters, anonymous functions can of course be used: ::

      >>> import heimdall
      >>> ...  # create config, load HERA tree
      >>> # retrieve one specific property by its id
      >>> heimdall.getProperties(tree, lambda e: e.get('id') == 'dc:title')
    """  # nopep8: E501
    container = get_node(tree, 'properties')
    return get_nodes(container, 'property', filter)


def createProperty(tree, id, **kwargs):
    r"""Creates a single property.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param id: (:py:class:`str`) Property unique identifier
    :param \**kwargs: (:py:class:`dict`, optional) -- Keyword arguments, see below.
    :Keyword arguments:
        * **type** (:py:class:`str`, optional, default: ``text``) -- Property type
        * **name** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Human-readable name
        * **description** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Human-readable documentation
        * **uri** (:py:class:`list` of :py:class:`str`, optional) -- URI list
    :return: Property that was just created
    :rtype: :py:class:`heimdall.elements.Property`

    This function can be used to add a new property to a database.
    Elements created by ``createProperty`` will always be added to the ``<properties/>`` container element.

    :Usage examples:

    In its simplest usage, ``createProperty`` simply creates a new ``<property id='xxx'/>`` element: ::

      >>> import heimdall
      >>> ...  # create config
      >>> tree = heimdall.getDatabase(config)  # load HERA tree
      >>> heimdall.createProperty(tree, id='xxx')  # create a new property
      >>> # the following child is now added to the properties list:
      >>> # <property id='xxx' />

    Each property identifier must be unique among all properties.
    Thus, calling ``createProperty`` with an ``id`` already in use by another property in the same database will fail.

    Additional supported parameters are ``type``, ``name``, ``description``, and ``uri``.
    Each of these parameters creates appropriate children for the property.
    Here is an example: ::

      >>> import heimdall
      >>> ...  # create config, load HERA tree
      >>> heimdall.createProperty(tree,
      >>>     id='dc:title', name='Title',
      >>>     uri=[
      >>>         'http://purl.org/dc/terms/title',
      >>>         'http://purl.org/dc/terms/alternative',
      >>>         'http://nakala.fr/terms#title'
      >>>     ])
      >>> # the following property is now added to the properties list:
      >>> # <property id='dc:title'>
      >>> #     <type>text</type>
      >>> #     <name>Title</name>
      >>> #     <uri>http://purl.org/dc/terms/title</uri>
      >>> #     <uri>http://purl.org/dc/terms/alternative</uri>
      >>> #     <uri>http://nakala.fr/terms#title</uri>
      >>> # </property>

    Please note that ``name`` and ``description`` can be localized, if they are of type :py:class:`dict` instead of :py:class:`str` (:py:class:`dict` keys are language codes).
    The following example shows property localization: ::

      >>> import heimdall
      >>> ...  # create HERA element tree
      >>> heimdall.createProperty(tree, id='dc:title',
      >>>      name={
      >>>          'de': "Titel",
      >>>          'en': "Title",
      >>>          'fr': "Titre",
      >>>      },
      >>>      description={
      >>>          'en': "A name given to the resource.",
      >>>          'fr': "Un nom donné à la ressource.",
      >>>      })
      >>> # the following XML element is now added to the ``<properties/>`` container element:
      >>> # <property id='dc:title'>
      >>> #     <type>text</type>
      >>> #     <name xml:lang='de'>Titel</name>
      >>> #     <name xml:lang='en'>Title</name>
      >>> #     <name xml:lang='fr'>Titre</name>
      >>> #     <description xml:lang='en'>A name given to the resource.</description>
      >>> #     <description xml:lang='fr'>Un nom donné à la ressource.</description>
      >>> # </property>
    """  # nopep8: E501
    container = create_container(tree, 'properties')
    # Check that property unique id (pid) does not already exist
    if getProperty(tree, lambda n: n.get('id') == id) is not None:
        raise ValueError(f"Property id '{id}' already exists")
    # Create property
    node = Property(id=id)
    node.type = kwargs.get('type', 'text')
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
    container.append(node)
    return node


def replaceProperty(property, **kwargs):
    """Replaces an existing property.

    .. ERROR::
       This feature is not implemented yet.
       This can be either due to lack of resources, lack of demand, because it wouldn't be easily maintenable, or any combination of these factors.

       Interested readers can submit a request to further this topic.
       See the ``CONTRIBUTING.rst`` file at the root of the repository for details.
    """  # nopep8: E501
    raise ValueError("TODO: Not Implemented")  # pragma: no cover


def updateProperty(property, **kwargs):
    r"""Updates a single property.

    :param property: (:py:class:`heimdall.elements.Property`) -- HERA property
    :param \**kwargs: (:py:class:`dict`, optional) -- Keyword arguments, see below.
    :Keyword arguments:
        * **id** (:py:class:`str`, optional) -- Property identifier
        * **type** (:py:class:`str`, optional) -- Property type
        * **name** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Human-readable name
        * **description** (:py:class:`str`\ \|\ :py:class:`dict`, optional) -- Human-readable documentation
        * **uri** (:py:class:`list` of :py:class:`str`, optional) -- URI list
    :return: Property that was just updated
    :rtype: :py:class:`heimdall.elements.Property`

    This function can be used to update an existing property.

    :Usage examples:

    Any or all of ``updateProperty`` parameters can be used to update ``property``: ::

      >>> import heimdall
      >>> ...  # load HERA tree
      >>> p = heimdall.getProperty(tree, lambda x: x.get('id') == 'title')
      >>> heimdall.updateProperty(p, name='Label')

    Please note that ``name`` and ``description`` can be localized, if they are of type :py:class:`dict` instead of :py:class:`str` (:py:class:`dict` keys are language codes).
    The following example shows property localization: ::

      >>> import heimdall
      >>> ...  # load HERA element tree
      >>> p = heimdall.getProperty(tree, ...)
      >>> heimdall.updateProperty(p,
      >>>      name={
      >>>          'de': "Titel",
      >>>          'en': "Title",
      >>>          'fr': "Titre",
      >>>      },
      >>>      description={
      >>>          'en': "A name given to the resource.",
      >>>          'fr': "Un nom donné à la ressource.",
      >>>      })
    """  # nopep8: E501
    VALUES = ['id', ]
    _maybe_update_values(property, VALUES, **kwargs)
    CHILDREN = ['type', 'name', 'description', 'uri', ]
    for key in CHILDREN:
        try:
            value = kwargs[key]
            setattr(property, key, value)
        except KeyError:
            pass  # nothing to do
    return property


def deleteProperty(tree, filter):
    """Deletes a single property.

    :param tree: (:py:class:`heimdall.elements.Root`) -- HERA element tree
    :param filter: (:py:class:`function`) -- Filtering function
    :return: None
    :rtype: :py:class:`NoneType`

    This function can be used to delete properties from ``tree``.
    It performs the property deletion "in place"; in other words, parameter ``tree`` is directly modified, and this function returns nothing.

    If ``filter`` returns no result, this function does nothing, and does not raise any error.

    This method doesn't delete any metadata, nor any attribute, referencing the deleted property.
    All elements referencing this property, if any, will become invalid.
    They should either be deleted or fixed accordingly.

    :Usage example: ::

      >>> import heimdall
      >>> ...  # create config, load HERA tree
      >>> # delete a property using its unique id
      >>> heimdall.deleteProperty(tree, lambda e: e.get('id') == '42')
    """  # nopep8: E501
    nodes = getProperties(tree, filter)
    container = get_container(tree, 'properties')
    for node in nodes:
        container.remove(node)


__copyright__ = "Copyright the pyHeimdall contributors."
__license__ = 'AGPL-3.0-or-later'
__all__ = [
    'getProperty', 'getProperties',
    'createProperty', 'deleteProperty',
    'replaceProperty', 'updateProperty',
    '__copyright__', '__license__',
    ]
