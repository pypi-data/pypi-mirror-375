from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generic, List, TypeVar

TId = TypeVar("TId")


class DomainError(Exception):
    """Base domain exception."""


@dataclass(frozen=True)
class DomainEvent:
    """Immutable domain event."""
    occurred_at: datetime = datetime.now(timezone.utc)

    @property
    def name(self):
        return self.__class__.__name__


class ValueObject:
    """Base for value objects (immutable in practice)."""
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __hash__(self) -> int:  # allow in sets/dicts
        return hash(tuple(sorted(self.__dict__.items())))


class Entity(Generic[TId]):
    id: TId


class AggregateRoot(Entity[TId]):
    """Aggregate root with domain event collection."""
    def __init__(self, *args, **kwargs) -> None:
        self._domain_events: List[DomainEvent] = []

    def _raise(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
