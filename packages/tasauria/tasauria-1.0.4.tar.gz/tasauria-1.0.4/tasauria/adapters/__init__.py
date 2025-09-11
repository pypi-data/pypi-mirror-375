# -*- coding: utf-8 -*-

"""
tasauria.adaptors
~~~~~~~~~~~~~~~~~~

Adaptor implementations for connecting to the TASauria server and marshalling commands.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

from tasauria.adapters.async_ import HTTPAdapter, WebSocketAdapter


__all__ = [
    'HTTPAdapter',
    'WebSocketAdapter'
]
