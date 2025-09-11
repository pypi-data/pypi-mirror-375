# -*- coding: utf-8 -*-

"""
tasauria.systems.nes
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Nintendo Entertainment System (1983) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


NES_SYSTEM_NAME = "NES"


@dataclasses.dataclass
class NESController(BizHawkInput):
    """
    Encapsulation of Nintendo Entertainment System controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False


@dataclasses.dataclass
class NESInput(BizHawkSystemInput):
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return NESController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
