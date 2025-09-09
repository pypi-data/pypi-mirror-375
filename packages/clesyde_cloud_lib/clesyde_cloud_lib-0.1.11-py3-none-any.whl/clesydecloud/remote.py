"""Manage remote UI connections."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
import random
import ssl
from typing import TYPE_CHECKING

import async_timeout  # noqa: TID251
from snitun.exceptions import SniTunConnectionError
from snitun.utils.aes import generate_aes_keyset
from snitun.utils.aiohttp_client import SniTunClientAioHttp

from .data import CloudConfig
from .status import CloudService
from .utils import gather_callbacks, periodic_coroutine, server_context_modern, retrieve_sn_from_pem_file

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clesydecloud import ClesydeCloud, _ClientT

# interval of seconds between each snitun refresh task restart
_REFRESH_SNITUN_TOKEN_INTERVAL_SEC = 300
# number of secs to wait for IoT response for token refresh, before asking again
_SNITUN_TOKEN_REFRESH_TIMEOUT_SEC = 30
# Remaining minutes before expiration threshold to trigger refresh
_SNITUN_TOKEN_EXPIRATION_LIMIT_MINS = 15

# Remote snitun server TCP port
_SNITUN_REMOTE_TCP_PORT = 8443


@dataclass
class SniTunTokenPayload:
    """Encapsulate snitun token information."""

    valid: int
    throttling: int
    token: str

@dataclass
class CertRefreshPayload:
    cert:str
    pkey:str


class RemoteAccess(CloudService):
    """Manages the remote connection using SniTun."""

    def __init__(self, cloud: ClesydeCloud[_ClientT]) -> None:
        """Initialize RemoteAccess class. Register cloud hooks."""
        self.cloud = cloud

        # Task to monitor snitun connection and to start reconnection on disconnect
        self.remote_client_reconnect_task: asyncio.Task | None = None
        # Task to check snitun token, and trigger its refresh depending on specified conditions
        self.periodic_snitun_token_refresh_task: asyncio.Task | None = None

        self.is_iot_connected: bool = False
        self._snitun_token_payload: SniTunTokenPayload | None = None
        self.snitun_client: SniTunClientAioHttp | None = None
        self.is_refreshing_snitun_token: bool = False

        self._aes_key: bytes | None = None
        self._aes_iv: bytes | None = None

        self._on_connect: list[Callable[[], Awaitable[None]]] = []
        self._on_disconnect: list[Callable[[], Awaitable[None]]] = []

        self.cloud.iot.register_on_connect(self.on_iot_connected)
        self.cloud.iot.register_on_disconnect(self.on_iot_disconnected)
        self.cloud.register_on_stop(self.on_stop)

    def register_on_connect(self, on_connect_cb: Callable[[], Awaitable[None]]) -> None:
        """Register an async on_connect callback."""
        self._on_connect.append(on_connect_cb)

    def register_on_disconnect(
        self,
        on_disconnect_cb: Callable[[], Awaitable[None]],
    ) -> None:
        """Register an async on_disconnect callback."""
        self._on_disconnect.append(on_disconnect_cb)

    def _token_valid_to_mins(self) -> float:
        """Remaining time in minutes before snitun token expiration.

        :return: float
        """
        if self._snitun_token_payload is not None:
            converted_valid = datetime.fromtimestamp(
                self._snitun_token_payload.valid, UTC
            )
            current_time_utc = datetime.now(UTC)
            return (converted_valid - current_time_utc).total_seconds() / 60
        # else
        return 0

    def _is_token_expired(self) -> bool:
        """Snitun token expiration is lower than the defined threshold _SNITUN_TOKEN_EXPIRATION_LIMIT_MINS.

        :return: bool
        """
        delta_min = self._token_valid_to_mins()
        if delta_min < _SNITUN_TOKEN_EXPIRATION_LIMIT_MINS:
            return True
        # else
        return False

    async def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with acme certificate."""
        context = server_context_modern()

        # We can not get here without this being set, but mypy does not know that.
        # assert self._acme is not None
        await self.cloud.run_executor(
            context.load_cert_chain,
            self.cloud.config.remote_cert_file(self.cloud),
            self.cloud.config.remote_key_file(self.cloud),
        )
        return context

    async def on_iot_connected(self):
        """Prepare for reconnection. Callback called on iot connected."""

        self.is_iot_connected = True
        if self.periodic_snitun_token_refresh_task is None:
            self.periodic_snitun_token_refresh_task = self.cloud.run_task(
                # no re-entrance, has the periodic_coroutine wait for coroutine to end,
                # before starting a new cycle
                periodic_coroutine(
                    _REFRESH_SNITUN_TOKEN_INTERVAL_SEC,
                    self._refresh_snitun_token,
                    start_immediately=True,
                )
            )

    async def on_iot_disconnected(self):
        """Refresh the token if needed. Callback called when iot is disconnected."""
        self.is_iot_connected = False
        if self.periodic_snitun_token_refresh_task is not None:
            self.periodic_snitun_token_refresh_task.cancel()

    async def on_stop(self):
        """Stop the snitun client. Callback called when cloud stack is stopped."""
        await self._stop_snitun_client()

    async def _refresh_snitun_token(self):
        """Refresh Snitun token."""
        _LOGGER.debug("Checking for expired snitun token")
        token_has_expired = self._is_token_expired()
        if (
            not self.is_refreshing_snitun_token
            and self.is_iot_connected
            and (self._snitun_token_payload is None or token_has_expired)
        ):
            if token_has_expired:
                _LOGGER.debug("Missing or expired snitun token, refreshing it")
            self.is_refreshing_snitun_token = True
            aes_key, aes_iv = generate_aes_keyset()
            self._aes_key = aes_key
            self._aes_iv = aes_iv
            # important: snitun expect keyset value (bytes) to be encoded
            # as hexadecimal string in the fernet token
            payload: str = json.dumps(
                {"aesKey": self._aes_key.hex(), "aesIv": self._aes_iv.hex()}
            )
            _LOGGER.debug("sending new token request")
            remote_token_topic = f"c/d/{self.cloud.client.device_sn}/remotetoken/req"
            self.cloud.iot.publish(remote_token_topic, payload, 0, False)

            await asyncio.sleep(_SNITUN_TOKEN_REFRESH_TIMEOUT_SEC)
            self.is_refreshing_snitun_token = False

    async def on_new_snitun_token(self, message_payload: str):
        """Process the new snitun token."""

        _LOGGER.debug("Received new snitun token")
        if self.is_refreshing_snitun_token:
            self.is_refreshing_snitun_token = False
            try:
                payload = json.loads(message_payload)
                self._snitun_token_payload = SniTunTokenPayload(
                    valid=payload["valid"],
                    throttling=payload["throttling"],
                    token=payload["token"],
                )
                _LOGGER.debug(
                    "New snitun token received, valid for %.2f minutes",
                    self._token_valid_to_mins(),
                )

            except json.JSONDecodeError as e:
                _LOGGER.error("Received invalid snitun token (%s)", e)
                self._snitun_token_payload = None
            except OSError as e:
                _LOGGER.error("Unknown error with new snitun token (%s)", e)
                self._snitun_token_payload = None

            if self._snitun_token_payload is not None:
                _LOGGER.info("Start or recycle Snitun client")
                await self._recycle_snitun_client()

        else:
            _LOGGER.debug(
                "New token ignored, as it seems to be from an old/previous request"
            )

    async def _recycle_snitun_client(self) -> None:
        _LOGGER.debug("Recycling Snitun client")
        await self._stop_snitun_client()
        await self._start_snitun_client()

    async def _stop_snitun_client(self):
        if self.remote_client_reconnect_task is not None:
            self.remote_client_reconnect_task.cancel()
            self.remote_client_reconnect_task = None

        if self.snitun_client is not None and self.snitun_client.is_connected:
            await self.snitun_client.disconnect()
        if self._on_disconnect:
            await gather_callbacks(_LOGGER, "on_disconnect", self._on_disconnect)

    async def _start_snitun_client(self):
        context = await self._create_ssl_context()
        self.snitun_client = SniTunClientAioHttp(
            self.cloud.client.aiohttp_runner,
            context,
            snitun_server=self.cloud.config.remote_endpoint,
            snitun_port=_SNITUN_REMOTE_TCP_PORT,
        )

        # Important : callback set must be the handler not the coroutine
        await self.snitun_client.start(False, self._recycle_snitun_client)
        self.cloud.run_task(self._connect_snitun_client())

    async def _connect_snitun_client(self):
        if self.snitun_client is not None and not self.snitun_client.is_connected:
            _LOGGER.debug("snitun connecting")
            try:
                async with async_timeout.timeout(30):
                    await self.snitun_client.connect(
                        fernet_key=self._snitun_token_payload.token.encode(),
                        aes_key=self._aes_key,
                        aes_iv=self._aes_iv,
                        throttling=self._snitun_token_payload.throttling,
                    )
                    if self._on_connect:
                        await gather_callbacks(_LOGGER, "on_connect", self._on_connect)
                    _LOGGER.info("Snitun connected")
                    _LOGGER.info(
                        "Device available here: https://%s:%s",
                        self.cloud.config.access_point,
                        _SNITUN_REMOTE_TCP_PORT,
                    )
            except TimeoutError:
                _LOGGER.error("Timeout connecting to snitun server")
            except SniTunConnectionError as err:
                _LOGGER.error("Failed to connect to snitun server (%s)", err)
            finally:
                # start retry reconnection task if :
                # - no snitun client,
                # - no reconnect task,
                # - and snitun token NOT expired
                if (
                    self.snitun_client
                    and not self.remote_client_reconnect_task
                    and not self._is_token_expired()
                ):
                    _LOGGER.debug("creating automatic reconnect task")
                    self.remote_client_reconnect_task = self.cloud.run_task(self._reconnect_snitun_client())

                # Disconnect if the instance is mark as insecure (token expired) and we're in reconnect mode
                elif self.remote_client_reconnect_task and self._is_token_expired():
                    _LOGGER.debug("connection error, and token expired, recycle server")
                    self.cloud.run_task(self._recycle_snitun_client())

    async def _reconnect_snitun_client(self):
        """Automatically reconnect after disconnect."""
        try:
            while True:
                if self.snitun_client is not None and self.snitun_client.is_connected:
                    await self.snitun_client.wait()  # wait for disconnect
                    _LOGGER.debug("Snitun disconnected, will try to reconnect")

                # wait a little bit before trying to reconnect
                wait_for_retry = random.randint(1, 15)
                _LOGGER.debug(f"Snitun client wait {wait_for_retry} seconds before retrying connection")
                await asyncio.sleep(wait_for_retry)
                await self._connect_snitun_client()
        except asyncio.CancelledError as error:
            _LOGGER.debug("CancelledError, ending remote access (%s)", error)
            pass
        finally:
            _LOGGER.debug("Close remote client reconnect guard")
            self.remote_client_reconnect_task = None

    def is_connected(self) -> bool:
        return self.snitun_client is not None and self.snitun_client.is_connected

    def on_request_cert_refresh(self, serial_number: str):
        _LOGGER.debug("Received cert rotation message")
        cert_file = self.cloud.config.remote_cert_file(self.cloud)
        current_sn = retrieve_sn_from_pem_file(cert_file)
        if serial_number != current_sn:
            _LOGGER.debug("Must update certificate file")

            payload: str = json.dumps({"remoteCertSn": serial_number})
            _LOGGER.debug("sending remote cert retrieval request")
            remote_cert_refresh_topic = f"c/d/{self.cloud.client.device_sn}/remotecr/req"
            self.cloud.iot.publish(remote_cert_refresh_topic, payload, 0, False)

        else:
            _LOGGER.debug("Same certificate file, nothing to do")

    async def on_received_cert_refresh(self, message_payload:str):
        try:
            _LOGGER.debug("Received cert rotation message")
            payload = json.loads(message_payload)
            cert_refresh = CertRefreshPayload(
                cert=payload["cert"],
                pkey=payload["pkey"],
            )
            _LOGGER.debug("Saving new certificate")
            CloudConfig.update_remote_cert(self.cloud.path(), cert_refresh.cert, cert_refresh.pkey)
            _LOGGER.debug("Restarting remote client")
            await self._recycle_snitun_client()

        except json.JSONDecodeError as e:
            _LOGGER.error("Received invalid cert refresh message (%s)", e)
        except OSError as e:
            _LOGGER.error("Unknown error with cert refresh message (%s)", e)




