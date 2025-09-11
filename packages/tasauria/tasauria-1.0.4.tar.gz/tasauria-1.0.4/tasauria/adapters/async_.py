# -*- coding: utf-8 -*-

"""
tasauria.adapters.async_
~~~~~~~~~~~~~~~~~~~~~~~~~

Async (asyncio) implementations of TASauria adapters

:copyright: (c) 2025-present Devon (scarlet.cafe) R
:license: MIT, see LICENSE for more details.

"""

import asyncio
import json
import logging
import typing

import aiohttp
import yarl

from tasauria.commands import Command, PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput
from tasauria.exceptions import AdapterDisconnected, TASauriaServerError


LOG = logging.getLogger("tasauria.adapters.async")

AsyncAdapterOrSubclass = typing.TypeVar("AsyncAdapterOrSubclass", bound="AsyncAdapter")


class AsyncAdapter:
    """
    Abstract base class for asynchronous TASauria adapters
    """

    @classmethod
    async def connect(
        cls: typing.Type[AsyncAdapterOrSubclass],
        url: typing.Union[yarl.URL, str]
    ) -> AsyncAdapterOrSubclass:
        """
        Creates an adapter of this kind by connecting to a URL.
        """

        raise NotImplementedError()

    async def close(
        self
    ) -> None:
        """
        Performs any cleanup that's required to 'stop' this adapter.
        """

        raise NotImplementedError()

    def closed(
        self
    ) -> bool:
        """
        Returns whether this adapter is closed or not.
        """

        raise NotImplementedError()

    async def execute_command(
        self,
        command: typing.Type[Command[PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput]],
        **kwargs: PythonCommandInput
    ) -> PythonCommandOutput:
        """
        Uses this adapter's implementation to marshal, send, await receipt, and unmarshal a command and its response.
        """

        raise NotImplementedError()


class HTTPAdapter(AsyncAdapter):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        url: yarl.URL,
    ):
        self._session: aiohttp.ClientSession = session
        self._url = url
        self._sequence_1: int = 0
        self._sequence_2: int = 0

    def next_sequence_id(
        self
    ) -> typing.Tuple[int, int]:
        """
        Generates a sequenced message ID to use for tracking simultaneous requests.

        The way we do this is way more conservative than is actually necessary, but it should be pretty failure-proof.
        """

        sequence_id = (self._sequence_2, self._sequence_1)

        self._sequence_1 += 1
        if self._sequence_1 >= 8_000_000:
            self._sequence_2 += 1
            self._sequence_1 -= 8_000_000

        return sequence_id

    @classmethod
    async def connect(
        cls,
        url: typing.Union[yarl.URL, str]
    ) -> "HTTPAdapter":
        session = aiohttp.ClientSession()

        if not isinstance(url, yarl.URL):
            url = yarl.URL(url)

        async with session.post(
            url.with_path("/meta/ping"),
            json={}
        ) as request:
            response = await request.json()

        assert response.get('pong', None) is True

        return cls(
            session,
            url
        )

    async def close(
        self
    ) -> None:
        await self._session.close()

    def closed(
        self
    ) -> bool:
        return self._session.closed

    async def execute_command(
        self,
        command: typing.Type[Command[PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput]],
        **kwargs: typing.Any
    ) -> PythonCommandOutput:
        sequence_id = self.next_sequence_id()
        LOG.debug("HTTPAdapter marshalling input for %s %s", type(command).__name__, sequence_id)
        input_command, input_payload = command.marshal_input(**kwargs)

        LOG.debug("HTTPAdapter sending request for %s %s", type(command).__name__, sequence_id)
        async with self._session.post(
            self._url.with_path(input_command),
            json={
                "messageIdentifier": sequence_id,
                **input_payload
            }
        ) as request:
            LOG.debug("HTTPAdapter receiving response for %s %s", type(command).__name__, sequence_id)
            response = await request.json()

        if "error" in response:
            raise TASauriaServerError(response["error"])

        LOG.debug("HTTPAdapter unmarshalling output for %s %s", type(command).__name__, sequence_id)
        return command.unmarshal_output(response, **kwargs)


class WebSocketAdapter(AsyncAdapter):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        socket: aiohttp.ClientWebSocketResponse
    ):
        self._session: aiohttp.ClientSession = session
        self._socket: aiohttp.ClientWebSocketResponse = socket
        self._sequence_1: int = 0
        self._sequence_2: int = 0
        self._response_listeners: typing.Dict[
            typing.Tuple[int, int],
            asyncio.Future[typing.Dict[str, typing.Any]]
        ] = {}
        self._closed: asyncio.Event = asyncio.Event()
        self._close_complete: asyncio.Event = asyncio.Event()
        self._task = asyncio.create_task(self.loop())

    def next_sequence_id(
        self
    ) -> typing.Tuple[int, int]:
        """
        Generates a sequenced message ID to use for tracking simultaneous requests.

        The way we do this is way more conservative than is actually necessary, but it should be pretty failure-proof.
        """

        sequence_id = (self._sequence_2, self._sequence_1)

        self._sequence_1 += 1
        if self._sequence_1 >= 8_000_000:
            self._sequence_2 += 1
            self._sequence_1 -= 8_000_000

        return sequence_id

    async def loop(
        self
    ):
        cancel = asyncio.create_task(self._closed.wait())
        heartbeat_task = asyncio.create_task(asyncio.sleep(5))
        receive_future = asyncio.create_task(self._socket.receive())

        while not self._closed.is_set():
            LOG.debug("WebSocketAdapter loop waiting for event")
            done, _ = await asyncio.wait((
                receive_future,
                heartbeat_task,
                cancel
            ), return_when=asyncio.FIRST_COMPLETED)
            LOG.debug("WebSocketAdapter loop woken")

            if heartbeat_task in done:
                heartbeat_task = asyncio.create_task(asyncio.sleep(5))
                heartbeat_sequence = self.next_sequence_id()

                LOG.debug("WebSocketAdapter loop sending heartbeat PING %s", heartbeat_sequence)
                await self._socket.send_json({
                    "command": "/meta/ping",
                    "messageIdentifier": heartbeat_sequence,
                })

            if receive_future in done:
                LOG.debug("WebSocketAdapter loop collecting response")
                try:
                    response: aiohttp.WSMessage = await receive_future
                except aiohttp.WebSocketError:
                    break

                receive_future = asyncio.create_task(self._socket.receive())

                if response.type not in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):
                    LOG.debug("WebSocketAdapter loop received non-JSON message of type %s, discarding", response.type)
                    continue

                try:
                    payload: typing.Dict[str, typing.Any] = json.loads(response.data)
                except json.JSONDecodeError:
                    LOG.debug("WebSocketAdapter loop received message %s that wasn't valid JSON, discarding", response.type)
                    continue

                if "messageIdentifier" in payload:
                    message_id = payload["messageIdentifier"]

                    if isinstance(message_id, list):
                        message_id: typing.Tuple[int, ...] = tuple(message_id)

                    if payload.get("pong", None):
                        LOG.debug("WebSocketAdapter loop received PONG %s", message_id)

                    if message_id in self._response_listeners:
                        LOG.debug("WebSocketAdapter loop waking up task for %s", message_id)
                        self._response_listeners[message_id].set_result(payload)
                else:
                    LOG.debug("WebSocketAdapter loop got response with no identifier, discarding")

            if cancel in done:
                LOG.debug("WebSocketAdapter loop stopping because the adapter became closed")
                break

        await self._socket.close()
        await self._session.close()
        self._close_complete.set()

    @classmethod
    async def connect(
        cls,
        url: typing.Union[yarl.URL, str]
    ) -> "WebSocketAdapter":
        session = aiohttp.ClientSession()
        socket = await session.ws_connect(url)

        return cls(
            session,
            socket
        )

    async def close(
        self
    ) -> None:
        self._closed.set()
        # Wait up to one second for the loop to actually end
        await asyncio.wait_for(self._close_complete.wait(), 1.0)

    def closed(
        self
    ):
        return self._socket.closed

    async def execute_command(
        self,
        command: typing.Type[Command[PythonCommandInput, ServerCommandInput, ServerCommandOutput, PythonCommandOutput]],
        **kwargs: typing.Any
    ) -> PythonCommandOutput:
        if self._closed.is_set():
            raise AdapterDisconnected()

        sequence_id = self.next_sequence_id()
        LOG.debug("WebSocketAdapter marshalling input for %s %s", type(command).__name__, sequence_id)
        input_command, input_payload = command.marshal_input(**kwargs)

        # Create listener for this sequence ID in advance so we have no chance of missing it
        future: asyncio.Future[typing.Dict[str, typing.Any]] = asyncio.Future()
        self._response_listeners[sequence_id] = future

        LOG.debug("WebSocketAdapter sending request for %s %s", type(command).__name__, sequence_id)
        await self._socket.send_json({
            "command": input_command,
            "messageIdentifier": sequence_id,
            **input_payload
        })

        try:
            task = asyncio.create_task(asyncio.wait_for(future, 15.0))

            done, pending = await asyncio.wait((
                task,
                asyncio.create_task(self._closed.wait())
            ), return_when=asyncio.FIRST_COMPLETED)

            for pending_task in pending:
                pending_task.cancel()

            if task in done:
                LOG.debug("WebSocketAdapter receiving response for %s %s", type(command).__name__, sequence_id)
                response: ServerCommandOutput = typing.cast(
                    ServerCommandOutput,
                    await task
                )
            else:
                raise AdapterDisconnected()
        finally:
            self._response_listeners.pop(sequence_id, None)

        if "error" in response:
            raise TASauriaServerError(response["error"])

        LOG.debug("WebSocketAdapter unmarshalling output for %s %s", type(command).__name__, sequence_id)
        return command.unmarshal_output(response, **kwargs)
