# -*- coding: utf-8 -*-

"""
tasauria.systems.genesis
~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the SEGA Genesis/Mega Drive (1988) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


GENESIS_SYSTEM_NAME = "GEN"


@dataclasses.dataclass
class GenesisController(BizHawkInput):
    """
    Encapsulation of SEGA Genesis controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    c_button: typing.Annotated[bool, BizHawkName("C")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False


@dataclasses.dataclass
class GenesisInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return GenesisController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
