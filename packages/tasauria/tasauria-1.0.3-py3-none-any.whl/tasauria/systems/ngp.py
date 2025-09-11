# -*- coding: utf-8 -*-

"""
tasauria.systems.ngp
~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Neo Geo Pocket (1998) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


NEO_GEO_POCKET_SYSTEM_NAME = "NGP"


@dataclasses.dataclass
class NeoGeoPocketController(BizHawkInput):
    """
    Encapsulation of Nintendo Entertainment System controller inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    option: typing.Annotated[bool, BizHawkName("Option")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False


@dataclasses.dataclass
class NeoGeoPocketInput(BizHawkSystemInput):
    power: typing.Annotated[bool, BizHawkName("Power")] = False
    reset: typing.Annotated[bool, BizHawkName("Reset")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return NeoGeoPocketController

    @staticmethod
    def get_max_controller_count() -> int:
        return 1
