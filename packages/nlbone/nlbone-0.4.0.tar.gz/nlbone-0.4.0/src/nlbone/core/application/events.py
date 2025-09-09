from typing import Iterable, Sequence
from nlbone.core.domain.base import AggregateRoot, DomainEvent
from nlbone.core.ports.event_bus import EventBusPort

def collect_events(*aggregates: Iterable[AggregateRoot]) -> list[DomainEvent]:
    events: list[DomainEvent] = []
    for agg in aggregates:
        if isinstance(agg, AggregateRoot):
            events.extend(agg.pull_events())
        else:
            for a in agg:
                events.extend(a.pull_events())
    return events

def publish_events(bus: EventBusPort, events: Sequence[DomainEvent]) -> None:
    if events: bus.publish(events)
