# -*- coding: utf-8 -*-

"""
tasauria.systems.amiga
~~~~~~~~~~~~~~~~~~~~~~~

Classes and functions related to the Commodora Amiga (1985) system.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import dataclasses
import typing

from tasauria.types import BizHawkName, BizHawkInput, BizHawkSystemInput


AMIGA_SYSTEM_NAME = "Amiga"


@dataclasses.dataclass
class AmigaController(BizHawkInput):
    """
    Encapsulation of Commodore Amiga controller inputs.
    """

    # Either mouse
    mouse_x: typing.Annotated[int, BizHawkName("Mouse X")] = 0
    mouse_y: typing.Annotated[int, BizHawkName("Mouse Y")] = 0
    mouse_left: typing.Annotated[bool, BizHawkName("Mouse Left Button")] = False
    mouse_middle: typing.Annotated[bool, BizHawkName("Mouse Middle Button")] = False
    mouse_right: typing.Annotated[bool, BizHawkName("Mouse Right Button")] = False
    # Or stick
    joystick_up: typing.Annotated[bool, BizHawkName("Joystick Up")] = False
    joystick_down: typing.Annotated[bool, BizHawkName("Joystick Down")] = False
    joystick_left: typing.Annotated[bool, BizHawkName("Joystick Left")] = False
    joystick_right: typing.Annotated[bool, BizHawkName("Joystick Right")] = False
    joystick_1: typing.Annotated[bool, BizHawkName("Joystick Button 1")] = False
    joystick_2: typing.Annotated[bool, BizHawkName("Joystick Button 2")] = False
    joystick_3: typing.Annotated[bool, BizHawkName("Joystick Button 3")] = False


@dataclasses.dataclass
class AmigaInput(BizHawkSystemInput):
    next_drive: typing.Annotated[bool, BizHawkName("Next Drive")] = False
    next_slot: typing.Annotated[bool, BizHawkName("Next Slot")] = False
    insert_disk: typing.Annotated[bool, BizHawkName("Insert Disk")] = False
    eject_disk: typing.Annotated[bool, BizHawkName("Eject Disk")] = False
    key_backquote: typing.Annotated[bool, BizHawkName("Key Backquote")] = False
    key_1: typing.Annotated[bool, BizHawkName("Key 1")] = False
    key_2: typing.Annotated[bool, BizHawkName("Key 2")] = False
    key_3: typing.Annotated[bool, BizHawkName("Key 3")] = False
    key_4: typing.Annotated[bool, BizHawkName("Key 4")] = False
    key_5: typing.Annotated[bool, BizHawkName("Key 5")] = False
    key_6: typing.Annotated[bool, BizHawkName("Key 6")] = False
    key_7: typing.Annotated[bool, BizHawkName("Key 7")] = False
    key_8: typing.Annotated[bool, BizHawkName("Key 8")] = False
    key_9: typing.Annotated[bool, BizHawkName("Key 9")] = False
    key_0: typing.Annotated[bool, BizHawkName("Key 0")] = False
    key_minus: typing.Annotated[bool, BizHawkName("Key Minus")] = False
    key_equals: typing.Annotated[bool, BizHawkName("Key Equal")] = False
    key_backslash: typing.Annotated[bool, BizHawkName("Key Backslash")] = False
    key_np_0: typing.Annotated[bool, BizHawkName("Key NP 0")] = False
    key_q: typing.Annotated[bool, BizHawkName("Key Q")] = False
    key_w: typing.Annotated[bool, BizHawkName("Key W")] = False
    key_e: typing.Annotated[bool, BizHawkName("Key E")] = False
    key_r: typing.Annotated[bool, BizHawkName("Key R")] = False
    key_t: typing.Annotated[bool, BizHawkName("Key T")] = False
    key_y: typing.Annotated[bool, BizHawkName("Key Y")] = False
    key_u: typing.Annotated[bool, BizHawkName("Key U")] = False
    key_i: typing.Annotated[bool, BizHawkName("Key I")] = False
    key_o: typing.Annotated[bool, BizHawkName("Key O")] = False
    key_p: typing.Annotated[bool, BizHawkName("Key P")] = False
    key_left_bracket: typing.Annotated[bool, BizHawkName("Key Left Bracket")] = False
    key_right_bracket: typing.Annotated[bool, BizHawkName("Key Right Bracket")] = False
    key_np_1: typing.Annotated[bool, BizHawkName("Key NP 1")] = False
    key_np_2: typing.Annotated[bool, BizHawkName("Key NP 2")] = False
    key_np_3: typing.Annotated[bool, BizHawkName("Key NP 3")] = False
    key_a: typing.Annotated[bool, BizHawkName("Key A")] = False
    key_s: typing.Annotated[bool, BizHawkName("Key S")] = False
    key_d: typing.Annotated[bool, BizHawkName("Key D")] = False
    key_f: typing.Annotated[bool, BizHawkName("Key F")] = False
    key_g: typing.Annotated[bool, BizHawkName("Key G")] = False
    key_h: typing.Annotated[bool, BizHawkName("Key H")] = False
    key_j: typing.Annotated[bool, BizHawkName("Key J")] = False
    key_k: typing.Annotated[bool, BizHawkName("Key K")] = False
    key_l: typing.Annotated[bool, BizHawkName("Key L")] = False
    key_semicolon: typing.Annotated[bool, BizHawkName("Key Semicolon")] = False
    key_quote: typing.Annotated[bool, BizHawkName("Key Quote")] = False
    key_number_sign: typing.Annotated[bool, BizHawkName("Key Number Sign")] = False
    key_np_4: typing.Annotated[bool, BizHawkName("Key NP 4")] = False
    key_np_5: typing.Annotated[bool, BizHawkName("Key NP 5")] = False
    key_np_6: typing.Annotated[bool, BizHawkName("Key NP 6")] = False
    key_less: typing.Annotated[bool, BizHawkName("Key Less")] = False
    key_z: typing.Annotated[bool, BizHawkName("Key Z")] = False
    key_x: typing.Annotated[bool, BizHawkName("Key X")] = False
    key_c: typing.Annotated[bool, BizHawkName("Key C")] = False
    key_v: typing.Annotated[bool, BizHawkName("Key V")] = False
    key_b: typing.Annotated[bool, BizHawkName("Key B")] = False
    key_n: typing.Annotated[bool, BizHawkName("Key N")] = False
    key_m: typing.Annotated[bool, BizHawkName("Key M")] = False
    key_comma: typing.Annotated[bool, BizHawkName("Key Comma")] = False
    key_period: typing.Annotated[bool, BizHawkName("Key Period")] = False
    key_slash: typing.Annotated[bool, BizHawkName("Key Slash")] = False
    key_np_delete: typing.Annotated[bool, BizHawkName("Key NP Delete")] = False
    key_np_7: typing.Annotated[bool, BizHawkName("Key NP 7")] = False
    key_np_8: typing.Annotated[bool, BizHawkName("Key NP 8")] = False
    key_np_9: typing.Annotated[bool, BizHawkName("Key NP 9")] = False
    key_space: typing.Annotated[bool, BizHawkName("Key Space")] = False
    key_backspace: typing.Annotated[bool, BizHawkName("Key Backspace")] = False
    key_tab: typing.Annotated[bool, BizHawkName("Key Tab")] = False
    key_np_enter: typing.Annotated[bool, BizHawkName("Key NP Enter")] = False
    key_return: typing.Annotated[bool, BizHawkName("Key Return")] = False
    key_escape: typing.Annotated[bool, BizHawkName("Key Escape")] = False
    key_delete: typing.Annotated[bool, BizHawkName("Key Delete")] = False
    key_np_sub: typing.Annotated[bool, BizHawkName("Key NP Sub")] = False
    key_up: typing.Annotated[bool, BizHawkName("Key Up")] = False
    key_down: typing.Annotated[bool, BizHawkName("Key Down")] = False
    key_right: typing.Annotated[bool, BizHawkName("Key Right")] = False
    key_left: typing.Annotated[bool, BizHawkName("Key Left")] = False
    key_f1: typing.Annotated[bool, BizHawkName("Key F1")] = False
    key_f2: typing.Annotated[bool, BizHawkName("Key F2")] = False
    key_f3: typing.Annotated[bool, BizHawkName("Key F3")] = False
    key_f4: typing.Annotated[bool, BizHawkName("Key F4")] = False
    key_f5: typing.Annotated[bool, BizHawkName("Key F5")] = False
    key_f6: typing.Annotated[bool, BizHawkName("Key F6")] = False
    key_f7: typing.Annotated[bool, BizHawkName("Key F7")] = False
    key_f8: typing.Annotated[bool, BizHawkName("Key F8")] = False
    key_f9: typing.Annotated[bool, BizHawkName("Key F9")] = False
    key_f10: typing.Annotated[bool, BizHawkName("Key F10")] = False
    key_np_left_paren: typing.Annotated[bool, BizHawkName("Key NP Left Paren")] = False
    key_np_right_paren: typing.Annotated[bool, BizHawkName("Key NP Right Paren")] = False
    key_np_div: typing.Annotated[bool, BizHawkName("Key NP Div")] = False
    key_np_mul: typing.Annotated[bool, BizHawkName("Key NP Mul")] = False
    key_np_add: typing.Annotated[bool, BizHawkName("Key NP Add")] = False
    key_help: typing.Annotated[bool, BizHawkName("Key Help")] = False
    key_left_shift: typing.Annotated[bool, BizHawkName("Key Left Shift")] = False
    key_right_shift: typing.Annotated[bool, BizHawkName("Key Right Shift")] = False
    key_caps_lock: typing.Annotated[bool, BizHawkName("Key Caps Lock")] = False
    key_ctrl: typing.Annotated[bool, BizHawkName("Key Ctrl")] = False
    key_left_alt: typing.Annotated[bool, BizHawkName("Key Left Alt")] = False
    key_right_alt: typing.Annotated[bool, BizHawkName("Key Right Alt")] = False
    key_left_amiga: typing.Annotated[bool, BizHawkName("Key Left Amiga")] = False
    key_right_amiga: typing.Annotated[bool, BizHawkName("Key Right Amiga")] = False

    @staticmethod
    def get_controller_type() -> typing.Type[BizHawkInput]:
        return AmigaController

    @staticmethod
    def get_max_controller_count() -> int:
        return 2
