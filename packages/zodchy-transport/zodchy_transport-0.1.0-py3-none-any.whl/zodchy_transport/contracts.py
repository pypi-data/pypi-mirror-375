import abc
import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DispatchableMessage(abc.ABC):
    id: uuid.UUID
    payload: dict
    
@dataclass(frozen=True, slots=True, kw_only=True)
class RabbitMessage(DispatchableMessage):
    routing_key: str | None = None
    exchange: str | None = None
    queue: str | None = None
    persist: bool = False
