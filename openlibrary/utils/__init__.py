"""Generic utilities"""

import re
from subprocess import PIPE, Popen, STDOUT
from typing import TypeVar, Iterable, List

to_drop = set(''';/?:@&=+$,<>#%"{}|\\^[]`\n\r''')


def str_to_key(s):
    return ''.join(c if c != ' ' else '_' for c in s.lower() if c not in to_drop)


def finddict(dicts, **filters):
    """Find a dictionary that matches given filter conditions.

    >>> dicts = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    >>> sorted(finddict(dicts, x=1).items())
    [('x', 1), ('y', 2)]
    """
    for d in dicts:
        if all(d.get(k) == v for k, v in filters.items()):
            return d


re_solr_range = re.compile(r'\[.+\bTO\b.+\]', re.I)
re_bracket = re.compile(r'[\[\]]')


def escape_bracket(q):
    if re_solr_range.search(q):
        return q
    return re_bracket.sub(lambda m: '\\' + m.group(), q)


T = TypeVar('T')


def uniq(values: Iterable[T], key=None) -> list[T]:
    """Returns the unique entries from the given values in the original order.

    The value of the optional `key` parameter should be a function that takes
    a single argument and returns a key to test the uniqueness.
    TODO: Moved this to core/utils.py
    """
    key = key or (lambda x: x)
    s = set()
    result = []
    for v in values:
        k = key(v)
        if k not in s:
            s.add(k)
            result.append(v)
    return result


def dicthash(d):
    """Dictionaries are not hashable. This function converts dictionary into nested
    tuples, so that it can hashed.
    """
    if isinstance(d, dict):
        return tuple((k, dicthash(d[k])) for k in sorted(d))
    elif isinstance(d, list):
        return tuple(dicthash(v) for v in d)
    else:
        return d


author_olid_re = re.compile(r'^OL\d+A$')


def is_author_olid(s):
    """Case sensitive check for strings like 'OL123A'."""
    return bool(author_olid_re.match(s))


work_olid_re = re.compile(r'^OL\d+W$')


def is_work_olid(s):
    """Case sensitive check for strings like 'OL123W'."""
    return bool(work_olid_re.match(s))


def extract_numeric_id_from_olid(olid):
    """
    >>> extract_numeric_id_from_olid("OL123W")
    '123'
    >>> extract_numeric_id_from_olid("/authors/OL123A")
    '123'
    """
    if '/' in olid:
        olid = olid.split('/')[-1]
    if olid.lower().startswith('ol'):
        olid = olid[2:]
    if not is_number(olid[-1].lower()):
        olid = olid[:-1]
    return olid


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_software_version():  # -> str:
    cmd = "git rev-parse --short HEAD --".split()
    return str(Popen(cmd, stdout=PIPE, stderr=STDOUT).stdout.read().decode().strip())
