# -*- coding: utf-8 -*-

"""
tasauria.systems.vectrex
~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Smith Engineering Vectrex (1982) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


VECTREX_SYSTEM_NAME = "VEC"


@dataclasses.dataclass
class VectrexController(BizHawkInput):
    """
    Encapsulation of Vectrex controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    button_1: typing.Annotated[bool, BizHawkName("Button 1")] = False
    button_2: typing.Annotated[bool, BizHawkName("Button 1")] = False
    button_3: typing.Annotated[bool, BizHawkName("Button 1")] = False
    button_4: typing.Annotated[bool, BizHawkName("Button 1")] = False


@dataclasses.dataclass
class VectrexInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return VectrexController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
