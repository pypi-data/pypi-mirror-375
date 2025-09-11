# -*- coding: utf-8 -*-

"""
tasauria.exceptions
~~~~~~~~~~~~~~~~~~~~

Errors that can occur during TASauria usage.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""


class TASauriaException(Exception):
    pass


class AdapterDisconnected(TASauriaException):
    pass


class NoBindingsAvailable(TASauriaException):
    pass


class TASauriaServerError(TASauriaException):
    pass
