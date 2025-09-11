# -*- coding: utf-8 -*-

"""
tasauria.systems.master_system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the SEGA Master System (1986) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


MASTER_SYSTEM_SYSTEM_NAME = "SMS"


@dataclasses.dataclass
class MasterSystemController(BizHawkInput):
    """
    Encapsulation of SEGA Master System controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    b1: typing.Annotated[bool, BizHawkName("B1")] = False
    b2: typing.Annotated[bool, BizHawkName("B2")] = False


@dataclasses.dataclass
class MasterSystemInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False
    pause: typing.Annotated[bool, BizHawkName("Pause")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return MasterSystemController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
