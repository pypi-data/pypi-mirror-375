from __future__ import annotations
from typing import Callable, Iterable, Protocol
from nlbone.core.domain.base import DomainEvent

class EventBusPort(Protocol):
    def publish(self, events: Iterable[DomainEvent]) -> None: ...
    def subscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None: ...
