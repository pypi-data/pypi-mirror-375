"""Handle the communication with AWS IoT Core."""

from __future__ import annotations

import asyncio
from asyncio import CancelledError, Event, Queue
from collections.abc import Awaitable, Callable
import logging
import random
import ssl
from typing import TYPE_CHECKING, Final, Optional

from aiomqtt import Client, MqttError, ProtocolVersion, Will

from .iot_message import IotMessage
from .status import CloudService
from .utils import gather_callbacks, server_context_modern

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT


payload_online: Final = '{"state":"ONLINE"}'
payload_offline: Final = '{"state":"OFFLINE"}'


class IoT(CloudService):
    """Manages the communication with IoT Core."""

    def __init__(self, cloud: ClesydeCloud[_ClientT], iot_message: IotMessage) -> None:
        """Initiaze the IoT class."""
        self.cloud = cloud
        self._iot_message: IotMessage = iot_message

        self._client: Optional[Client] = None  # noqa: UP007
        self._publish_queue: (
            Queue[tuple[str, int | float | str | bytes, int, bool]] | None
        ) = None
        self._is_connected: Event | None = None
        self._task: Optional[asyncio.Task | None] = None  # noqa: UP007
        self._listening_task: Optional[asyncio.Task | None] = None  # noqa: UP007

        self._on_connect: list[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: list[Callable[[], Awaitable[None]]] = []
        self._con_retries: int = 0
        self._wait_for_con_retry_task: Optional[asyncio.Task | None] = None  # noqa: UP007
        self._context = None

        # Register start/stop
        self.cloud.register_on_start(self.start)
        self.cloud.register_on_stop(self.stop)

    def register_on_connect(self, on_connect_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_connect callback."""
        self._on_connect.append(on_connect_cb)

    def register_on_disconnect(
        self,
        on_disconnect_cb: Callable[[], Awaitable[None]],
    ) -> None:
        """Register an async on_disconnect callback."""
        self._on_disconnect.append(on_disconnect_cb)

    async def start(self) -> None:
        """Start the connection."""
        self._context = await self._create_ssl_context()

        self._is_connected = Event()
        if self._task is None:
            _LOGGER.info("Creating IoT Task")
            self._task = self.cloud.run_task(self._mqtt_task())

    async def stop(self) -> None:
        """Stop the connection."""
        _LOGGER.debug("Disconnecting")
        if self._listening_task is not None:
            self._listening_task.cancel()
            self._listening_task = None

        if self._wait_for_con_retry_task is not None:
            self._wait_for_con_retry_task.cancel()
            self._wait_for_con_retry_task = None

    async def _wait_before_connect(self) -> None:
        if self._con_retries == 0:
            self._wait_for_con_retry_task = None
            return

        seconds = 2 ** min(4, self._con_retries) + random.randint(
            0, self._con_retries * 4
        )
        self._wait_for_con_retry_task = self.cloud.run_task(asyncio.sleep(seconds))
        _LOGGER.info("Waiting %d seconds before retrying", seconds)
        await self._wait_for_con_retry_task
        self._wait_for_con_retry_task = None

    async def _listen_task(self):
        if self._client is not None:
            _LOGGER.debug("Waiting for IoT Message")
            async for message in self._client.messages:
                await self._iot_message.router(message)

    async def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with acme certificate."""
        context = server_context_modern()

        # We can not get here without this being set, but mypy does not know that.
        # assert self._acme is not None
        await self.cloud.run_executor(
            context.load_cert_chain,
            self.cloud.config.iot_cert_file(self.cloud),
            self.cloud.config.iot_key_file(self.cloud),
        )
        await self.cloud.run_executor(
            context.load_verify_locations,
            self.cloud.config.iot_ca_file(self.cloud),
        )
        return context

    async def _mqtt_task(self):
        self._is_connected = Event()
        shutdown = False
        self._con_retries = 0

        while not shutdown:
            await self._wait_before_connect()
            if self._con_retries > 0:
                _LOGGER.info("Connecting (retry %d)", self._con_retries)
            else:
                _LOGGER.info("Connecting")
            self._con_retries += 1

            try:
                last_will = Will(
                    topic=self._iot_message.status_topic, payload=payload_offline
                )

                self._client = Client(
                    hostname=self.cloud.config.iot_endpoint,  # "iot.remote-sandbox.clesyde.com"
                    port=8883,
                    identifier=self.cloud.config.iot_thing_name,
                    protocol=ProtocolVersion.V5,
                    transport="tcp",
                    will=last_will,
                    tls_context=self._context
                )

                async with self._client:
                    _LOGGER.debug("Connected successfully!")
                    self._con_retries = 0
                    self._publish_queue = Queue()
                    self._is_connected.set()

                    _LOGGER.debug("Topics subscription")
                    subscription_result = [
                        (await self._client.subscribe(topic), topic)
                        for topic in self._iot_message.subscriptions()
                    ]
                    # noqa: TODO: report any subscription error
                    _LOGGER.debug(subscription_result)
                    _LOGGER.debug("Subscribed to topics")
                    self._listening_task = self.cloud.run_task(self._listen_task())

                    if self._on_connect:
                        await gather_callbacks(_LOGGER, "on_connect", self._on_connect)

                    try:
                        # signal that we are online
                        _LOGGER.debug("Sending online status")
                        await self._client.publish(
                            self._iot_message.status_topic, payload_online, 0, False
                        )

                        while True:
                            topic, value, qos, retain = await self._publish_queue.get()
                            await self._client.publish(topic, value, qos, retain)
                            self._publish_queue.task_done()

                    except CancelledError:
                        _LOGGER.debug("CancelledError, shutdown mqtt task")
                        shutdown = True

                        if self._task is not None:
                            _LOGGER.debug("Sending offline status")
                            # signal that we are offline
                            await self._client.publish(
                                self._iot_message.status_topic,
                                payload_offline,
                                0,
                                False,
                            )
                            self._task.cancel()
                            self._task = None

            except MqttError as e:
                _LOGGER.debug("Mqtt error")
                _LOGGER.error(e)
            except OSError as ex:
                _LOGGER.debug("OSError")
                _LOGGER.error(ex)
            finally:
                self._publish_queue = None
                if self._is_connected is not None:
                    self._is_connected.clear()

                if self._on_disconnect:
                    await gather_callbacks(
                        _LOGGER, "on_disconnect", self._on_disconnect
                    )

            if not shutdown:
                _LOGGER.debug("Looping _mqtt_task")

        _LOGGER.debug("Leaving _mqtt_task")

    def publish(self, topic: str, value: float | str | bytes, qos: int, retain: bool):
        """Publish a message."""
        if self._publish_queue is not None:
            self._publish_queue.put_nowait((topic, value, qos, retain))

    def is_connected(self):
        return self._is_connected is not None and self._is_connected.is_set()
