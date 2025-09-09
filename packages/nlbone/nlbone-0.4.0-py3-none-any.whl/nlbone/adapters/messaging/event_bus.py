from __future__ import annotations
from collections import defaultdict
from typing import Callable, Dict, Iterable, List
from nlbone.core.domain.base import DomainEvent
from nlbone.core.ports.event_bus import EventBusPort

class InMemoryEventBus(EventBusPort):
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[DomainEvent], None]]] = defaultdict(list)

    def publish(self, events: Iterable[DomainEvent]) -> None:
        for evt in events:
            for h in self._handlers.get(evt.name, []):
                try:
                    h(evt)
                except Exception:
                    pass

    def subscribe(self, event_name: str, handler: Callable[[DomainEvent], None]) -> None:
        self._handlers[event_name].append(handler)
