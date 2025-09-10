# -*- coding: utf-8 -*-
import heimdall
import os as _os
import re as _re
from sys import version_info as _py
from urllib.parse import urlparse
from ..decorators import get_database, create_database
LENGTH_PREFIX = 'len:'


@create_database(['sql:mariadb', 'sql:mysql', ])
def dump(tree, url, **options):
    r"""Serialize a HERA elements tree into a MariaDB/MySQL dump like file

    :param tree: HERA elements tree
    :param url: Path of the SQL dump file to create
    :param \**options: (optional) Keyword arguments, see below.
    :Keyword arguments:
        * **allow_multivalues** (``bool``) -- (optional, default: ``True``)
          If ``True``, multiple values for the same entity attribute will be
          put in the same SQL column, separated by ``multivalue_separator``.
          If ``False``, this function will raise an error.
          should any attribute have a ``max`` greater than 1.
        * **multivalue_separator** (``str``) -- (optional, default: ``,``)
          "Character" separating multiple values for the same attribute
          in a given entity; used only if ``allow_multivalues`` is ``True``.
        * **engine** (``str``) -- (optional, default: ``InnoDB``)
          Storage engine. If ``None``, no storage engine will be set.
          See: https://mariadb.com/docs/server/server-usage/storage-engines ,
          https://dev.mysql.com/doc/refman/en/storage-engines.html .
        * **force_utf8** (``bool``) -- (optional, default: ``True``)
          If ``True``, `utf8` charset and `utf8_general_ci` collation
          will be set as default.

    .. WARNING::
       Dumping repeatable attributes is not properly implemented yet.
       It may be in the future, but it's currently not a critical feature.

       If you repeat metadata in your database and use this function, it is
       advised to double check the resulting dump and, should you be unhappy
       we it, contact us to bump this feature to a higher priority.
       See ``CONTRIBUTING`` document for details.
    """
    path = url
    if _os.path.exists(path):
        raise ValueError(f"File '{path}' already exists")

    allow = options.get('allow_multivalues', True)
    comma = options.get('multivalue_separator', ',')
    engine = options.get('engine', 'InnoDB')
    utf8 = options.get('force_utf8', True)
    entities = heimdall.getEntities(tree)
    primary_keys, foreign_keys = _get_pointers(tree, entities)
    with open(path, 'w', newline='') as f:
        f.write(f"{_pre_everything()}\n")
        for entity in entities:
            eid = entity.get('id')
            attributes = heimdall.getAttributes(entity)
            items = heimdall.getItems(tree, lambda n: n.get('eid') == eid)
            pk = primary_keys.get(eid, set())
            fk = foreign_keys.get(eid, dict())
            f.write(f"\n{_pre_create_table(eid)}\n")
            f.write(f"{_create_table(tree, eid, attributes, pk, fk, allow, engine, utf8)}\n")  # nopep8: E501
            f.write(f"{_pre_dump_data(eid)}\n")
            f.write(f"{_dump_data(items, eid, attributes, comma)}\n")
            f.write(f"{_post_dump_data()}\n")


def _pre_everything():
    text = "-- SQL dump, from a HERA database, using pyHeimdall\n"
    text += "-- ------------------------------------------------------\n"
    text += f"-- pyHeimdall version	{heimdall.__version__}"
    return text


def _pre_create_table(eid, drop=True):
    comment = f"--\n-- Table structure for table `{eid}`\n--"
    drop_table = f"\nDROP TABLE IF EXISTS `{eid}`;" if drop else ""
    return comment + drop_table


def _create_table(tree, eid, attributes, pk, fk, allow_multivalues, engine, utf8):  # nopep8: E501
    text = f"CREATE TABLE `{eid}` (\n"
    for attribute in attributes:
        (aid, pid) = _get_identifiers(attribute)
        if aid is None and pid is None:
            continue  # this unused attribute won't be part of the dump
        _id = aid if aid is not None else pid
        max = attribute.get('max')
        max = int(max) if max else None
        if not allow_multivalues and (max is None or max > 1):
            fault = f"{eid}.{aid}.max={max}"
            raise ValueError(f"Repeatable attributes not supported ({fault})")
        min = int(attribute.get('min') or 0)
        min = "NOT NULL" if min > 0 else "DEFAULT NULL"
        type = _get_sql_type(tree, attribute)
        text += f"`{_id}` {type} {min},\n"
    for aid in pk:
        text += f"PRIMARY KEY ({aid}),\n"
    for aid, targets in fk.items():
        if len(targets) > 1:
            fault = f"{eid}.{aid}"
            raise ValueError(f"Repeatable pointers not supported ({fault})")
        target_eid = next(iter(targets))
        target_aids = targets[target_eid]
        if len(target_aids) > 1:
            fault = f"{eid}.{aid}"
            raise ValueError(f"Repeatable pointers not supported ({fault})")
        target_aid = next(iter(target_aids))
        text += f"FOREIGN KEY ({aid}) REFERENCES {target_eid}({target_aid}),\n"
    if text.endswith(',\n'):
        text = text[:-2] + '\n'  # remove last comma
    str_engine = f" ENGINE={engine}" if engine else ""
    str_utf8 = " DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci" if utf8 else ""
    text += f"){str_engine}{str_utf8};"
    return text


def _get_identifiers(attribute):
    return (attribute.get('id'), attribute.get('pid'))


def _get_type(tree, attribute):
    type_node = heimdall.util.get_node(attribute, 'type')
    if type_node is not None:
        type_ = type_node.text
    else:
        pid = attribute.get('pid')
        property_ = heimdall.getProperty(tree, lambda n: n.get('id') == pid)
        type_node = heimdall.util.get_node(property_, 'type')
        if type_node is not None:
            type_ = type_node.text
        else:
            type_ = 'text'
    return type_


def _get_sql_type(tree, attribute):
    type_ = _get_type(tree, attribute)
    if type_ == 'datetime':
        return 'date'
    if type_ == 'number':
        return 'int'  # TODO unsigned
    rules = heimdall.util.get_nodes(attribute, 'rule')
    length = 255
    for rule in rules:
        if rule.text.startswith(LENGTH_PREFIX):
            length = int(rule.text[len(LENGTH_PREFIX):])
    if length > 1:
        return f'varchar({length})'
    return 'char(1)'


def _get_pointers(tree, entities):
    def _merge_dicts_sets(dst, src):
        for key, src_set in src.items():
            dst_set = dst.get(key, set())
            dst_set.update(src_set)
            dst[key] = dst_set

    foreign_keys = dict()
    primary_keys = dict()
    for entity in entities:
        eid = entity.get('id')
        attributes = heimdall.getAttributes(entity)
        for attribute in attributes:
            type_ = _get_type(tree, attribute)
            targets = _get_pointer_targets(type_)
            if not targets or len(targets) < 1:
                continue
            aid = attribute.get('id')  # TODO check None
            attrs = foreign_keys.get(eid, dict())
            fks = attrs.get(aid, dict())
            _merge_dicts_sets(fks, targets)
            attrs[aid] = fks
            foreign_keys[eid] = attrs
            _merge_dicts_sets(primary_keys, targets)
    return primary_keys, foreign_keys


def _get_pointer_targets(expr):
    if not expr.startswith('@'):
        return None
    targets = expr[1:].split(',')
    results = dict()
    for target in targets:
        parts = target.split('.')
        if len(parts) < 2:
            continue  # syntax error
        eid = parts[0]
        aid = '.'.join(parts[1:])
        aids = results.get(eid, set())
        aids.add(aid)
        results[eid] = aids
    return results


def _pre_dump_data(eid, lock=True):
    comment = f"--\n-- Dumping data for table `{eid}`\n--"
    lock_table = f"\nLOCK TABLE `{eid}` WRITE;" if lock else ""
    return comment + lock_table


def _dump_data(items, eid, attributes, multivalues_separator):
    if len(items) == 0:
        return f"-- No data in table `{eid}`"
    text = f"INSERT INTO `{eid}` VALUES "
    dumps = list()
    for item in items:
        values = list()
        for attribute in attributes:
            values.append(_dump_value(item, attribute, multivalues_separator))
        dumps.append(f"({','.join(values)})")
    text += ','.join(dumps)
    text += ";"
    return text


def _dump_value(item, attribute, multivalues_separator):
    (aid, pid) = _get_identifiers(attribute)
    values = list()
    if aid is not None:
        if pid is not None:
            values = heimdall.getValues(item, pid=pid, aid=aid)
        else:
            values = heimdall.getValues(item, aid=aid)
    else:
        if pid is not None:
            values = heimdall.getValues(item, pid=pid)
    values = [f"'{v}'" for v in values]
    if len(values) < 1:
        return 'NULL'
    return multivalues_separator.join(values)


def _post_dump_data(lock=True):
    return "UNLOCK TABLES;"
