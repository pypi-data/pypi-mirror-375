# -*- coding: utf-8 -*-

"""
tasauria.systems
~~~~~~~~~~~~~~~~~

Classes and functions that wrap the different systems BizHawk supports.

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import typing

from tasauria.exceptions import NoBindingsAvailable
from tasauria.types import BizHawkInput, TASauriaJoypadPayload

from tasauria.systems.amiga import AMIGA_SYSTEM_NAME, AmigaController, AmigaInput
from tasauria.systems.atari_2600 import ATARI_2600_SYSTEM_NAME, Atari2600Controller, Atari2600Input
from tasauria.systems.atari_7800 import ATARI_7800_SYSTEM_NAME, Atari7800Controller, Atari7800Input
from tasauria.systems.atari_lynx import ATARI_LYNX_SYSTEM_NAME, AtariLynxInput
from tasauria.systems.c64 import COMMODORE_64_SYSTEM_NAME, Commodore64Controller, Commodore64Input
from tasauria.systems.colecovision import COLECOVISION_SYSTEM_NAME, ColecoVisionController, ColecoVisionInput
from tasauria.systems.gb import GAMEBOY_SYSTEM_NAME, GAMEBOY_COLOR_SYSTEM_NAME, GameBoyInput
from tasauria.systems.gba import GAMEBOY_ADVANCE_SYSTEM_NAME, GameBoyAdvanceInput
from tasauria.systems.genesis import GENESIS_SYSTEM_NAME, GenesisController, GenesisInput
from tasauria.systems.intellivision import INTELLIVISION_SYSTEM_NAME, IntellivisionController, IntellivisionInput
from tasauria.systems.master_system import MASTER_SYSTEM_SYSTEM_NAME, MasterSystemController, MasterSystemInput
from tasauria.systems.n3ds import NINTENDO_3DS_SYSTEM_NAME, Nintendo3DSInput
from tasauria.systems.n64 import NINTENDO_64_SYSTEM_NAME, Nintendo64Controller, Nintendo64Input
from tasauria.systems.nds import NINTENDO_DS_SYSTEM_NAME, NintendoDSInput
from tasauria.systems.nes import NES_SYSTEM_NAME, NESController, NESInput
from tasauria.systems.ngp import NEO_GEO_POCKET_SYSTEM_NAME, NeoGeoPocketController, NeoGeoPocketInput
from tasauria.systems.odyssey2 import ODYSSEY_2_SYSTEM_NAME, Odyssey2Controller, Odyssey2Input
from tasauria.systems.pcfx import PCFX_SYSTEM_NAME, PCFXController, PCFXInput
from tasauria.systems.psx import PLAYSTATION_SYSTEM_NAME, PlayStationController, PlayStationInput
from tasauria.systems.saturn import SATURN_SYSTEM_NAME, SaturnController, SaturnInput
from tasauria.systems.snes import SNES_SYSTEM_NAME, SNESController, SNESInput
from tasauria.systems.turbografx import TURBOGRAFX_SYSTEM_NAME, TurboGrafxController, TurboGrafxInput
from tasauria.systems.vectrex import VECTREX_SYSTEM_NAME, VectrexController, VectrexInput
from tasauria.systems.virtual_boy import VIRTUAL_BOY_SYSTEM_NAME, VirtualBoyController, VirtualBoyInput
from tasauria.systems.zx_spectrum import ZX_SPECTRUM_SYSTEM_NAME, ZXSpectrumController, ZXSpectrumInput


INPUT_MAPPING: typing.Dict[str, typing.Tuple[typing.Type[BizHawkInput], typing.Optional[typing.Type[BizHawkInput]]]] = {
    AMIGA_SYSTEM_NAME: (AmigaInput, AmigaController),
    ATARI_2600_SYSTEM_NAME: (Atari2600Input, Atari2600Controller),
    ATARI_7800_SYSTEM_NAME: (Atari7800Input, Atari7800Controller),
    ATARI_LYNX_SYSTEM_NAME: (AtariLynxInput, None),
    COMMODORE_64_SYSTEM_NAME: (Commodore64Input, Commodore64Controller),
    COLECOVISION_SYSTEM_NAME: (ColecoVisionInput, ColecoVisionController),
    GAMEBOY_SYSTEM_NAME: (GameBoyInput, None),
    GAMEBOY_COLOR_SYSTEM_NAME: (GameBoyInput, None),
    GAMEBOY_ADVANCE_SYSTEM_NAME: (GameBoyAdvanceInput, None),
    GENESIS_SYSTEM_NAME: (GenesisInput, GenesisController),
    INTELLIVISION_SYSTEM_NAME: (IntellivisionInput, IntellivisionController),
    MASTER_SYSTEM_SYSTEM_NAME: (MasterSystemInput, MasterSystemController),
    NINTENDO_3DS_SYSTEM_NAME: (Nintendo3DSInput, None),
    NINTENDO_64_SYSTEM_NAME: (Nintendo64Input, Nintendo64Controller),
    NINTENDO_DS_SYSTEM_NAME: (NintendoDSInput, None),
    NES_SYSTEM_NAME: (NESInput, NESController),
    NEO_GEO_POCKET_SYSTEM_NAME: (NeoGeoPocketInput, NeoGeoPocketController),
    ODYSSEY_2_SYSTEM_NAME: (Odyssey2Input, Odyssey2Controller),
    PCFX_SYSTEM_NAME: (PCFXInput, PCFXController),
    PLAYSTATION_SYSTEM_NAME: (PlayStationInput, PlayStationController),
    SATURN_SYSTEM_NAME: (SaturnInput, SaturnController),
    SNES_SYSTEM_NAME: (SNESInput, SNESController),
    TURBOGRAFX_SYSTEM_NAME: (TurboGrafxInput, TurboGrafxController),
    VECTREX_SYSTEM_NAME: (VectrexInput, VectrexController),
    VIRTUAL_BOY_SYSTEM_NAME: (VirtualBoyInput, VirtualBoyController),
    ZX_SPECTRUM_SYSTEM_NAME: (ZXSpectrumInput, ZXSpectrumController)
}


def parse_system_input(joypad: TASauriaJoypadPayload) -> BizHawkInput:
    """
    Converts a TASauria joypad payload (e.g. received from `/joypad/get`) into an input class of the
    appropriate type.
    """

    input_type = INPUT_MAPPING.get(joypad['system'], None)

    if input_type is None:
        raise NoBindingsAvailable("No bindings are available for system type '%s'. You must handle the input type manually." % joypad['system'])

    return input_type[0].from_dict(joypad['state'])


def parse_controller_input(joypad: TASauriaJoypadPayload) -> BizHawkInput:
    """
    Converts a TASauria controller-only joypad payload (e.g. received from `/joypad/get` with a controller
    argument) into an input class of the appropriate type.
    """

    input_type = INPUT_MAPPING.get(joypad['system'], None)

    if input_type is None:
        raise NoBindingsAvailable("No bindings are available for system type '%s'. You must handle the input type manually." % joypad['system'])

    if input_type[1] is None:
        raise NoBindingsAvailable("System type '%s' has bindings for the system but not individual controllers. You must handle the input type manually." % joypad['system'])

    return input_type[1].from_dict(joypad['state'])
