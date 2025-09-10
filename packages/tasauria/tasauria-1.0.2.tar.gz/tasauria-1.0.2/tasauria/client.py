# -*- coding: utf-8 -*-

"""
tasauria.client
~~~~~~~~~~~~~~~~

Implementation of the client

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import struct
import typing
from types import TracebackType

import yarl

from tasauria.adapters.async_ import AsyncAdapter, HTTPAdapter, WebSocketAdapter
from tasauria.commands import AnyCommand, Command, PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput
from tasauria.commands.client import ClientFrameStatusCommand, ClientFrameAdvanceCommand, ClientGameCommand, FrameStatus, GameInfo
from tasauria.commands.joypad import JoypadGetCommand, JoypadSetCommand
from tasauria.commands.memory import MemoryReadFloatCommand, MemoryReadIntegerCommand, MemoryReadRangeCommand, MemoryWriteFloatCommand, MemoryWriteIntegerCommand, MemoryWriteRangeCommand
from tasauria.commands.meta import MetaBatchCommand, MetaPingCommand
from tasauria.commands.movie import MovieInfo, MovieInfoCommand
from tasauria.commands.savestate import SavestateLoadSlotCommand, SavestateSaveSlotCommand
from tasauria.exceptions import AdapterDisconnected
from tasauria.types import BizHawkInput


class TASauria:
    def __init__(
        self,
        url: typing.Optional[typing.Union[yarl.URL, str]] = None,
        adapter_type: typing.Optional[typing.Type[AsyncAdapter]] = None,
    ):
        if url is None:
            url = "ws://127.0.0.1:20251/websocket"

        if not isinstance(url, yarl.URL):
            url = yarl.URL(url)

        self.adapter_type: typing.Type[AsyncAdapter]

        if adapter_type is None:
            if url.scheme.lower() in ('ws', 'wss'):
                self.adapter_type = WebSocketAdapter
            else:
                self.adapter_type = HTTPAdapter
        else:
            self.adapter_type = adapter_type

        self.url = url
        self.adapter: typing.Optional[AsyncAdapter] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(
        self,
        _exception_type: typing.Type[BaseException],
        _exception_value: BaseException,
        _exception_traceback: TracebackType,
    ):
        await self.close()
        return False

    async def _execute_command(
        self,
        command: typing.Type[Command[PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput]],
        **kwargs: typing.Any
    ) -> PythonCommandOutput:
        if self.adapter is None:
            raise AdapterDisconnected()

        return await self.adapter.execute_command(command, **kwargs)

    async def connect(self) -> None:
        if self.adapter is None:
            self.adapter = await self.adapter_type.connect(self.url)

    async def close(
        self
    ) -> None:
        if self.adapter is not None:
            await self.adapter.close()

    # === Commands ===
    # -- Meta --
    async def ping(
        self
    ) -> bool:
        return await self._execute_command(
            MetaPingCommand
        )

    async def batch_commands(
        self,
        commands: typing.Sequence[typing.Tuple[
            typing.Type[AnyCommand],
            typing.Dict[str, typing.Any]
        ]]
    ) -> typing.List[typing.Any]:
        return await self._execute_command(
            MetaBatchCommand,
            commands=commands
        )

    # -- Client --
    async def get_frame_status(
        self
    ) -> FrameStatus:
        return await self._execute_command(
            ClientFrameStatusCommand
        )

    async def frame_advance(
        self,
        unpause: bool = False
    ) -> FrameStatus:
        return await self._execute_command(
            ClientFrameAdvanceCommand,
            unpause=unpause
        )

    async def get_game_info(
        self
    ) -> GameInfo:
        return await self._execute_command(
            ClientGameCommand
        )

    # -- Joypad --
    async def get_joypad(
        self,
        controller: typing.Optional[int] = None,
        with_movie: bool = False,
        immediate: bool = False,
    ) -> BizHawkInput:
        return await self._execute_command(
            JoypadGetCommand,
            controller=controller,
            with_movie=with_movie,
            immediate=immediate
        )

    async def set_joypad(
        self,
        state: BizHawkInput,
        controller: typing.Optional[int] = None,
    ) -> BizHawkInput:
        return await self._execute_command(
            JoypadSetCommand,
            state=state,
            controller=controller,
        )

    # -- Memory write --
    async def read_u8_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=False,
            domain=domain
        )

    async def read_u8_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=True,
            domain=domain
        )

    async def read_i8_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=False,
            domain=domain
        )

    async def read_i8_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=True,
            domain=domain
        )

    async def read_u16_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=2,
            signed=False,
            little=False,
            domain=domain
        )

    async def read_u16_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=2,
            signed=False,
            little=True,
            domain=domain
        )

    async def read_i16_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=2,
            signed=True,
            little=False,
            domain=domain
        )

    async def read_i16_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=2,
            signed=True,
            little=True,
            domain=domain
        )

    async def read_u24_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=3,
            signed=False,
            little=False,
            domain=domain
        )

    async def read_u24_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=3,
            signed=False,
            little=True,
            domain=domain
        )

    async def read_i24_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=3,
            signed=True,
            little=False,
            domain=domain
        )

    async def read_i24_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=3,
            signed=True,
            little=True,
            domain=domain
        )

    async def read_u32_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=4,
            signed=False,
            little=False,
            domain=domain
        )

    async def read_u32_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=4,
            signed=False,
            little=True,
            domain=domain
        )

    async def read_i32_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=4,
            signed=True,
            little=False,
            domain=domain
        )

    async def read_i32_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryReadIntegerCommand,
            address=address,
            size=4,
            signed=True,
            little=True,
            domain=domain
        )

    async def read_u64_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack(">Q", buffer)[0]

    async def read_u64_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack("<Q", buffer)[0]

    async def read_i64_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack(">q", buffer)[0]

    async def read_i64_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack("<q", buffer)[0]

    async def read_f32_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> float:
        return await self._execute_command(
            MemoryReadFloatCommand,
            address=address,
            little=False,
            domain=domain
        )

    async def read_f32_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> float:
        return await self._execute_command(
            MemoryReadFloatCommand,
            address=address,
            little=True,
            domain=domain
        )

    async def read_f64_be(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> float:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack(">d", buffer)[0]

    async def read_f64_le(
        self,
        address: int,
        domain: typing.Optional[str] = None,
    ) -> float:
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=8,
            domain=domain
        )
        return struct.unpack("<d", buffer)[0]

    async def read_memory_range(
        self,
        address: int,
        size: int,
        domain: typing.Optional[str] = None,
    ) -> bytes:
        return await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=size,
            domain=domain
        )

    async def read_struct(
        self,
        address: int,
        format: str,
        domain: typing.Optional[str] = None,
    ) -> typing.Tuple[typing.Any, ...]:
        size = struct.calcsize(format)
        buffer: bytes = await self._execute_command(
            MemoryReadRangeCommand,
            address=address,
            size=size,
            domain=domain
        )
        return struct.unpack(format, buffer)

    async def read_structs(
        self,
        structs: typing.Sequence[typing.Tuple[int, str]],
        domain: typing.Optional[str] = None,
    ) -> typing.List[typing.Tuple[typing.Any, ...]]:
        commands: typing.List[
            typing.Tuple[typing.Type[typing.Any], typing.Dict[str, typing.Any]]
        ] = [
            (MemoryReadRangeCommand, {
                "address": address,
                "size": struct.calcsize(format),
                "domain": domain
            })
            for (address, format) in structs
        ]
        results: typing.List[bytes] = await self.batch_commands(commands)
        return [
            struct.unpack(format, result)
            for result, (_, format) in zip(results, structs)
        ]

    # -- Memory write --
    async def write_u8_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=False,
            data=data,
            domain=domain
        )

    async def write_u8_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=True,
            data=data,
            domain=domain
        )

    async def write_i8_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=False,
            data=data,
            domain=domain
        )

    async def write_i8_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=True,
            data=data,
            domain=domain
        )

    async def write_u16_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=2,
            signed=False,
            little=False,
            data=data,
            domain=domain
        )

    async def write_u16_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=2,
            signed=False,
            little=True,
            data=data,
            domain=domain
        )

    async def write_i16_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=2,
            signed=True,
            little=False,
            data=data,
            domain=domain
        )

    async def write_i16_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=2,
            signed=True,
            little=True,
            data=data,
            domain=domain
        )

    async def write_u24_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=3,
            signed=False,
            little=False,
            data=data,
            domain=domain
        )

    async def write_u24_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=3,
            signed=False,
            little=True,
            data=data,
            domain=domain
        )

    async def write_i24_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=3,
            signed=True,
            little=False,
            data=data,
            domain=domain
        )

    async def write_i24_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=3,
            signed=True,
            little=True,
            data=data,
            domain=domain
        )

    async def write_u32_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=False,
            data=data,
            domain=domain
        )

    async def write_u32_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=False,
            little=True,
            data=data,
            domain=domain
        )

    async def write_i32_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=False,
            data=data,
            domain=domain
        )

    async def write_i32_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        return await self._execute_command(
            MemoryWriteIntegerCommand,
            address=address,
            size=1,
            signed=True,
            little=True,
            data=data,
            domain=domain
        )

    async def write_u64_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack(">Q", data),
            domain=domain
        )
        return struct.unpack(">Q", buffer)[0]

    async def write_u64_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack("<Q", data),
            domain=domain
        )
        return struct.unpack("<Q", buffer)[0]

    async def write_i64_be(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack(">q", data),
            domain=domain
        )
        return struct.unpack(">q", buffer)[0]

    async def write_i64_le(
        self,
        address: int,
        data: int,
        domain: typing.Optional[str] = None,
    ) -> int:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack("<q", data),
            domain=domain
        )
        return struct.unpack("<q", buffer)[0]

    async def write_f32_be(
        self,
        address: int,
        data: float,
        domain: typing.Optional[str] = None,
    ) -> float:
        return await self._execute_command(
            MemoryWriteFloatCommand,
            address=address,
            little=False,
            data=data,
            domain=domain
        )

    async def write_f32_le(
        self,
        address: int,
        data: float,
        domain: typing.Optional[str] = None,
    ) -> float:
        return await self._execute_command(
            MemoryWriteFloatCommand,
            address=address,
            little=True,
            data=data,
            domain=domain
        )

    async def write_f64_be(
        self,
        address: int,
        data: float,
        domain: typing.Optional[str] = None,
    ) -> float:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack(">d", data),
            domain=domain
        )
        return struct.unpack(">d", buffer)[0]

    async def write_f64_le(
        self,
        address: int,
        data: float,
        domain: typing.Optional[str] = None,
    ) -> float:
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=8,
            data=struct.pack("<d", data),
            domain=domain
        )
        return struct.unpack("<d", buffer)[0]

    async def write_memory_range(
        self,
        address: int,
        size: int,
        data: bytes,
        domain: typing.Optional[str] = None,
    ) -> bytes:
        return await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=size,
            data=data,
            domain=domain
        )

    async def write_struct(
        self,
        address: int,
        format: str,
        *arguments: typing.Any,
        domain: typing.Optional[str] = None,
    ) -> typing.Tuple[typing.Any, ...]:
        size = struct.calcsize(format)
        buffer: bytes = await self._execute_command(
            MemoryWriteRangeCommand,
            address=address,
            size=size,
            data=struct.pack(format, *arguments),
            domain=domain
        )
        return struct.unpack(format, buffer)

    async def write_structs(
        self,
        structs: typing.Sequence[typing.Tuple[int, str, typing.Tuple[typing.Any, ...]]],
        domain: typing.Optional[str] = None,
    ) -> typing.List[typing.Tuple[typing.Any, ...]]:
        commands: typing.List[
            typing.Tuple[typing.Type[typing.Any], typing.Dict[str, typing.Any]]
        ] = [
            (MemoryWriteRangeCommand, {
                "address": address,
                "size": struct.calcsize(format),
                "data": struct.pack(format, *arguments),
                "domain": domain
            })
            for (address, format, arguments) in structs
        ]
        results: typing.List[bytes] = await self.batch_commands(commands)
        return [
            struct.unpack(format, result)
            for result, (_, format, _) in zip(results, structs)
        ]

    # -- Movie --
    async def get_movie_info(
        self,
    ) -> MovieInfo:
        return await self._execute_command(
            MovieInfoCommand
        )

    # -- Savestate --
    async def save_state_to_slot(
        self,
        slot: int,
        suppress_osd: bool = False
    ):
        return await self._execute_command(
            SavestateSaveSlotCommand,
            slot=slot,
            suppress_osd=suppress_osd
        )

    async def load_state_from_slot(
        self,
        slot: int,
        suppress_osd: bool = False
    ):
        return await self._execute_command(
            SavestateLoadSlotCommand,
            slot=slot,
            suppress_osd=suppress_osd
        )
