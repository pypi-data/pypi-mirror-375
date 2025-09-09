from __future__ import annotations
from typing import Any, Mapping, Optional

from dependency_injector import containers, providers

from nlbone.adapters.http_clients.uploadchi import UploadchiClient
from nlbone.adapters.http_clients.uploadchi_async import UploadchiAsyncClient
from nlbone.adapters.auth.keycloak import KeycloakAuthService
from nlbone.core.ports.files import FileServicePort, AsyncFileServicePort


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(strict=False)

    auth: providers.Singleton[KeycloakAuthService] = providers.Singleton(KeycloakAuthService, settings=config)
    file_service: providers.Singleton[FileServicePort] = providers.Singleton(UploadchiClient)
    afiles_service: providers.Singleton[AsyncFileServicePort] = providers.Singleton(UploadchiAsyncClient)


def create_container(settings: Optional[Any] = None) -> Container:
    c = Container()
    if settings is not None:
        if hasattr(settings, "model_dump"):
            c.config.from_dict(settings.model_dump())  # Pydantic v2
        elif hasattr(settings, "dict"):
            c.config.from_dict(settings.dict())  # Pydantic v1
        elif isinstance(settings, Mapping):
            c.config.from_dict(dict(settings))
        else:
            c.config.override(settings)
    return c
