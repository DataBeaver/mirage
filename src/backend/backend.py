import asyncio
import logging as log
import sys
import traceback
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

import hsluv
from appdirs import AppDirs

import nio

from . import __app_name__
from .errors import MatrixError
from .matrix_client import MatrixClient
from .models.items import Account, Device, Event, Member, Room, Upload
from .models.model_store import ModelStore

# Logging configuration
log.getLogger().setLevel(log.INFO)
nio.logger_group.level = nio.log.logbook.ERROR
nio.log.logbook.StreamHandler(sys.stderr).push_application()


class Backend:
    """Manage matrix clients and provide other useful general methods."""

    def __init__(self) -> None:
        self.appdirs = AppDirs(appname=__app_name__, roaming=True)

        from . import user_files
        self.saved_accounts = user_files.Accounts(self)
        self.ui_settings    = user_files.UISettings(self)
        self.ui_state       = user_files.UIState(self)
        self.history        = user_files.History(self)

        self.models = ModelStore(allowed_key_types={
            Account,             # Logged-in accounts
            (Device, str),       # Devices of user_id
            (Room,   str),       # Rooms for user_id
            (Upload, str),       # Uploads running in room_id
            (Member, str, str),  # Members for account user_id for room_id
            (Event,  str, str),  # Events for account user_id for room_id
        })

        self.clients: Dict[str, MatrixClient] = {}

        self.profile_cache: Dict[str, nio.ProfileGetResponse] = {}
        self.get_profile_locks: DefaultDict[str, asyncio.Lock] = \
                DefaultDict(asyncio.Lock)  # {user_id: lock}

        self.send_locks: DefaultDict[str, asyncio.Lock] = \
                DefaultDict(asyncio.Lock)  # {room_id: lock}

        from .media_cache import MediaCache
        cache_dir        = Path(self.appdirs.user_cache_dir)
        self.media_cache = MediaCache(self, cache_dir)


    def __repr__(self) -> str:
        return f"{type(self).__name__}(clients={self.clients!r})"


    # Clients management

    async def login_client(self,
        user:       str,
        password:   str,
        device_id:  Optional[str] = None,
        homeserver: str           = "https://matrix.org",
   ) -> str:
        """Create and register a `MatrixClient`, login and return a user ID."""

        client = MatrixClient(
            self, user=user, homeserver=homeserver, device_id=device_id,
        )

        try:
            await client.login(password)
        except MatrixError:
            await client.close()
            raise

        self.clients[client.user_id]         = client
        self.models[Account][client.user_id] = Account(client.user_id)
        return client.user_id


    async def resume_client(self,
                            user_id:    str,
                            token:      str,
                            device_id:  str,
                            homeserver: str = "https://matrix.org") -> None:
        """Create and register a `MatrixClient` with known account details."""

        client = MatrixClient(
            backend=self,
            user=user_id, homeserver=homeserver, device_id=device_id,
        )

        self.clients[user_id]         = client
        self.models[Account][user_id] = Account(user_id)

        await client.resume(user_id=user_id, token=token, device_id=device_id)


    async def load_saved_accounts(self) -> Tuple[str, ...]:
        """Call `resume_client` for all saved accounts in user config."""

        async def resume(user_id: str, info: Dict[str, str]) -> str:
            await self.resume_client(
                user_id    = user_id,
                token      = info["token"],
                device_id  = info["device_id"],
                homeserver = info["homeserver"],
            )
            return user_id

        return await asyncio.gather(*(
            resume(uid, info)
            for uid, info in (await self.saved_accounts.read()).items()
        ))


    async def logout_client(self, user_id: str) -> None:
        """Log a `MatrixClient` out and unregister it from our models."""

        client = self.clients.pop(user_id, None)
        if client:
            self.models[Account].pop(user_id, None)
            await client.logout()

        await self.saved_accounts.delete(user_id)


    async def get_client(self, user_id: str) -> MatrixClient:
        """Wait until a `MatrixClient` is registered in model and return it."""

        failures = 0

        while True:
            if user_id in self.clients:
                return self.clients[user_id]

            if failures and failures % 100 == 0:  # every 10s except first time
                log.warning(
                    "Client %r not found after %ds, stack trace:\n%s",
                    user_id, failures / 10, traceback.format_stack(),
                )

            await asyncio.sleep(0.1)
            failures += 1


    async def get_any_client(self) -> MatrixClient:
        """Return any healthy syncing `MatrixClient` registered in model."""

        failures = 0

        while True:
            for client in self.clients.values():
                if client.syncing:
                    return client

            if failures and failures % 300 == 0:
                log.warn(
                    "No healthy client found after %ds, stack trace:\n%s",
                    failures / 10, traceback.format_stack(),
                )

            await asyncio.sleep(0.1)
            failures += 1


    # Client functions that don't need authentification

    async def get_profile(self, user_id: str) -> nio.ProfileGetResponse:
        """Cache and return the matrix profile of `user_id`."""

        if user_id in self.profile_cache:
            return self.profile_cache[user_id]

        async with self.get_profile_locks[user_id]:
            client   = await self.get_any_client()
            response = await client.get_profile(user_id)

            if isinstance(response, nio.ProfileGetError):
                raise MatrixError.from_nio(response)

            self.profile_cache[user_id] = response
            return response


    async def thumbnail(
        self, server_name: str, media_id: str, width: int, height: int,
    ) -> nio.ThumbnailResponse:
        """Return thumbnail for a matrix media."""

        args     = (server_name, media_id, width, height)
        client   = await self.get_any_client()
        response = await client.thumbnail(*args)

        if isinstance(response, nio.ThumbnailError):
            raise MatrixError.from_nio(response)

        return response


    async def download(
        self, server_name: str, media_id: str,
    ) -> nio.DownloadResponse:
        """Return the content of a matrix media."""

        client   = await self.get_any_client()
        response = await client.download(server_name, media_id)

        if isinstance(response, nio.DownloadError):
            raise MatrixError.from_nio(response)

        return response


    # General functions

    @staticmethod
    def hsluv(hue: int, saturation: int, lightness: int) -> List[float]:
        """Convert HSLuv (0-360, 0-100, 0-100) to RGB (0-1, 0-1, 0-1) color."""

        return hsluv.hsluv_to_rgb([hue, saturation, lightness])


    async def load_settings(self) -> tuple:
        """Return parsed user config files."""

        from .user_files import Theme
        settings = await self.ui_settings.read()
        ui_state = await self.ui_state.read()
        history  = await self.history.read()
        theme    = await Theme(self, settings["theme"]).read()

        return (settings, ui_state, history, theme)


    async def get_flat_mainpane_data(self) -> List[Dict[str, Any]]:
        """Return a flat list of accounts and their joined rooms for QML."""

        data = []

        for account in sorted(self.models[Account].values()):
            data.append({
                "type":    "Account",
                "id":      account.user_id,
                "user_id": account.user_id,
                "data":    account.serialized,
            })

            for room in sorted(self.models[Room, account.user_id].values()):
                data.append({
                    "type":    "Room",
                    "id":      "/".join((account.user_id, room.room_id)),
                    "user_id": account.user_id,
                    "data":    room.serialized,
                })

        return data