# -*- coding: utf-8 -*-

"""
tasauria.systems.atari_lynx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Atari Lynx (1989) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput


ATARI_LYNX_SYSTEM_NAME = "Lynx"


@dataclasses.dataclass
class AtariLynxInput(BizHawkInput):
    """
    Encapsulation of Atari Lynx inputs.
    """

    up: typing.Annotated[bool, BizHawkName("Up")] = False
    down: typing.Annotated[bool, BizHawkName("Down")] = False
    left: typing.Annotated[bool, BizHawkName("Left")] = False
    right: typing.Annotated[bool, BizHawkName("Right")] = False
    start_button: typing.Annotated[bool, BizHawkName("Start")] = False
    select_button: typing.Annotated[bool, BizHawkName("Select")] = False
    a_button: typing.Annotated[bool, BizHawkName("A")] = False
    b_button: typing.Annotated[bool, BizHawkName("B")] = False
    option_1: typing.Annotated[bool, BizHawkName("Option 1")] = False
    option_2: typing.Annotated[bool, BizHawkName("Option 2")] = False
    pause: typing.Annotated[bool, BizHawkName("Pause")] = False
    power: typing.Annotated[bool, BizHawkName("Power")] = False
