import typing
import collections.abc

from faststream.rabbit import RabbitBroker

from ..contracts import RabbitMessage


class Broker(typing.Protocol):
    async def publish(self, message: dict, **settings):
        pass


class RabbitDispatcher:
    def __init__(self, dsn: str):
        self._broker = RabbitBroker(dsn)
        self._connected = False

    async def dispatch(
        self,
        *messages: RabbitMessage,
    ) -> collections.abc.AsyncIterable[RabbitMessage]:
        try:
            for message in messages:
                if await self._dispatch_one(message):
                    yield message
        except Exception as e:
            print(f"Failed to send message: {e}")
        finally:
            if self._connected:
                await self._broker.stop()
                
    async def _ensure_connection(self):
        if not self._connected:
            await self._broker.connect()
            self._connected = True

    async def _dispatch_one(self, message: RabbitMessage):
        await self._ensure_connection()

        if not message.queue and not message.exchange:
            raise ValueError("Either queue or exchange must be provided")

        if message.exchange:
            if not message.routing_key:
                raise ValueError(
                    "Routing key must be provided when exchange is provided"
                )
        payload = message.payload
        try:
            if message.exchange:
                await self._broker.publish(
                    payload,
                    exchange=message.exchange,
                    routing_key=message.routing_key,
                    persist=message.persist,
                )
            else:
                await self._broker.publish(
                    payload, queue=message.queue, persist=message.persist
                )

            print(f"Message sent to {message.queue}: {message}")
            return True

        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
