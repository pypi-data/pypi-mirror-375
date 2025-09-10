# -*- coding: utf-8 -*-
#
# mimeparser/__init__.py
#
"""
MIME Parser package
"""
__docformat__ = "restructuredtext en"
__author__ = 'Carl J. Nobile'
__email__ = 'carl.nobile@gmail.com'
__license__ = 'MIT License'
__credits__ = ''

__all__ = ('MIMEParser',)

from .mimeparser import MIMEParser


__version_info__ = {
    'major': 2,
    'minor': 0,
    'patch': 0,
    'releaselevel': 'final',
    'serial': 1
    }


def _get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = []
    vers.append("{major:d}".format(**__version_info__))
    vers.append("{minor:d}".format(**__version_info__))

    if __version_info__.get('patch', 0):
        vers.append("{patch:d}".format(**__version_info__))  # pragma: no cover

    result = '.'.join(vers)

    if __version_info__.get('releaselevel') != 'final' and not short:
        result += "{}{:d}".format(  # pragma: no cover
            __version_info__.get('releaselevel', 'a')[0],
            __version_info__.get('serial'))

    return result


__version__ = _get_version()
