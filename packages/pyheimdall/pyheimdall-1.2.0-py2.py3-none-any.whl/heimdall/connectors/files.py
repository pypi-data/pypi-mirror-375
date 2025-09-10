# -*- coding: utf-8 -*-
import heimdall
from ..util.tree import create_empty_tree
from ..decorators import get_database
from os import walk, listdir
from os.path import join, sep, isdir, isfile

"""
Provides connectors to local files and folders.

This module defines input and output connectors to local corpora.

:copyright: The pyHeimdall contributors.
:licence: Afero GPL, see LICENSE for more details.
:SPDX-License-Identifier: AGPL-3.0-or-later
"""  # nopep8: E501


@get_database(['files', 'files:local', ])
def getDatabase(**options):
    r"""Imports a database from local folders and files.

    This function does three things:

    1. search for files/folders (depending on a search strategy, see below) that can become database Items
    2. create an Item for each file/folder found
    3. call the ``on_item`` callback function (if any), mainly to populate each created Item with metadata

    :param \**options: Keyword arguments, see below.
    :Keyword arguments:
        * **url** (:py:class:`str`) -- Local path to a folder where items will be searched for
        * **format** (:py:class:`str`, optional) -- Always ``files`` or ``files:local``
        * **item_strategy** (:py:class:`function`, optional, default: :py:class:`OneItemPerFolder`) -- Item search function
        * **depth** (:py:class:`int`, optional, default: ``1``) -- Maximum depth (from ``url``) where items will be searched for
        * **on_item** (:py:class:`function`, optional) -- Item creation function
        * **item_eid** (:py:class:`str`, optional, default: ``item``) -- Entity ID of found items
        * **file_eid** (:py:class:`str`, optional, default: ``file``) -- Entity ID of files found for each item
    :return: HERA element tree
    :rtype: :py:class:`xml.etree.ElementTree.Element`

    :Usage examples:

    In its simplest usage, :py:class:`heimdall.connectors.files.getDatabase`
    simply creates a database containing one element ``<item eid='item' />``
    for each direct subfolder of the ``url`` folder, as long as one element
    ``<item eid='file' />`` for each file the subfolder contains.
    The ``item`` element will in turn have one pointer metadata
    (``<metadata pid='file' />``) for each file the subfolder contains. ::

      >>> import heimdall
      >>> tree = heimdall.getDatabase(format='files', url='./mycorpus/')

    If you want one item to be created for each *file* contained in ``url``,
    you just have to change the item search strategy: ::

      >>> import heimdall
      >>> from heimdall.files import OneItemPerFile
      >>> tree = heimdall.getDatabase(format='files', url='./mycorpus/', item_strategy=OneItemPerFile)

    By default, strategies :py:class:`OneItemPerFolder` and :py:class:`OneItemPerFile`
    only search direct children of root folder ``url``. You can change this
    behaviour using the ``depth`` parameter. For example, for infinite depth
    file search:

      >>> import heimdall
      >>> tree = heimdall.getDatabase(format='files', url='./mycorpus/', item_strategy=OneItemPerFile, depth=None)

    You can implement your own item searching logic by defining a function
    with the same profile as :py:class:`OneItemPerFolder` or
    :py:class:`OneItemPerFile` functions:

      >>> import heimdall
      >>>
      >>> def MyStrategy(item, max_depth):
      >>>    paths = list()
      >>>    # ... fill `paths` with `str` elements ...
      >>>    # /!\ each path should exist, of course
      >>>    return paths
      >>>
      >>> tree = heimdall.getDatabase(format='files', url='./mycorpus/', item_strategy=MyStrategy)

    By default, created items will only contain metadata based on existing files.
    You can complete each created item with additional metadata by defining
    a callback function and passing it as the ``on_item`` parameter:

      >>> import heimdall
      >>>
      >>> class Counter(object):
      >>>    count = 0
      >>>    def set_count(self, item, path):
      >>>       self.count += 1
      >>>       heimdall.createMetadata(item, str(self.count), pid='id')
      >>>
      >>> c = Counter()
      >>> tree = heimdall.getDatabase(format='files', url='./mycorpus/', on_item=c.set_count)

    You can change the entity ID (eid) of created elements using the
    ``item_eid`` and ``file_eid`` arguments.

    .. CAUTION::
       For future compability, this function shouldn't be directly called; as shown in the usage example above, it should only be used through :py:class:`heimdall.getDatabase`.
    """  # nopep8: E501
    url = options['url']
    item_strategy = options.get('item_strategy', OneItemPerFolder)
    depth = options.get('depth', 1)
    on_item = options.get('on_item', None)
    item_eid = options.get('item_eid', 'item')
    file_eid = options.get('file_eid', 'file')
    file_pointer = 'file'  # pointer metadata to 'file' element in 'item'

    paths = item_strategy(url, depth)
    tree = create_empty_tree()
    created_items_count = 0
    for path in paths:
        item = heimdall.createItem(tree, eid=item_eid)
        created_items_count += 1

        if on_item:
            on_item(item, path)

        if isdir(path):
            for file in listdir(path):
                p = join(path, file)
                if isfile(p):
                    heimdall.createMetadata(item, p, pid=file_pointer)
                    heimdall.createItem(tree, eid=file_eid, path=p)
        else:  # assume isfile(path) == True
            heimdall.createMetadata(item, path, pid=file_pointer)
            heimdall.createItem(tree, eid=file_eid, path=path)

    if created_items_count > 0:
        heimdall.util.update_entities(tree)
        e = heimdall.getEntity(tree, lambda e: e.get('id') == item_eid)
        a = heimdall.getAttribute(e, lambda a: a.get('pid') == file_pointer)
        a.type = f'@{file_eid}.path_attr'
    # else: don't bother, as update_entities won't create anything anyway
    return tree


def OneItemPerFolder(url, max_depth=1):
    """Item creation strategy: one item per folder.

    With this strategy, one item will be created for each non-empty subfolder
    of ``url`` whose depth is lesser than ``max_depth``.

    This item creation strategy is intended to serve as one of the possible
    parameters of :py:class:`heimdall.connectors.files.getDatabase`.

    :param url: (:py:class:`str`) --  Path to root folder
    :param max_depth: (:py:class:`int`, default ``1``) -- Maximum depth of items from ``url`` ; ``None`` for infinite depth
    :return: List of folder paths to items to be created
    :rtype: :py:class:`list` of :py:class:`str`
    """  # nopep8: E501
    paths = list()  # this will be returned
    if max_depth is not None and max_depth < 0:
        # return empty list if `max_depth` < 0
        return paths
    root_depth = url.rstrip(sep).count(sep)
    for path, dirnames, filenames in walk(url):
        depth = path.rstrip(sep).count(sep) - root_depth
        if depth == 0:
            continue  # ignore root folder
        if max_depth is not None and depth > max_depth:
            continue  # ignore subfolders with depth > max_depth
        paths.append(path)
    return paths


def OneItemPerFile(url, max_depth=1):
    """Item creation strategy: one item per file.

    With this strategy, one item will be created for each file contained
    in ``url`` whose depth is lesser than ``max_depth``.

    This item creation strategy is intended to serve as one of the possible
    parameters of :py:class:`heimdall.connectors.files.getDatabase`.

    :param url: (:py:class:`str`) --  Path to a folder
    :param max_depth: (:py:class:`int`, default ``1``) --  Maximum depth of items from ``url`` ; ``None`` for infinite depth
    :return: List of file paths to items to be created
    :rtype: :py:class:`list` of :py:class:`str`
    """  # nopep8: E501
    paths = list()  # this will be returned
    if max_depth is not None and max_depth < 0:
        # return empty list if `max_depth` < 0
        return paths
    root_depth = url.rstrip(sep).count(sep)
    for path, dirnames, filenames in walk(url):
        depth = path.rstrip(sep).count(sep) - root_depth
        if max_depth is not None and depth >= max_depth:
            continue  # ignore subfolders with depth >= max_depth
        for filename in filenames:
            paths.append(join(path, filename))

    return paths
