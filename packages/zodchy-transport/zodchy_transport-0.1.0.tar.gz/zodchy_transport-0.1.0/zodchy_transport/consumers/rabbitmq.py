from collections.abc import Callable
from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker, RabbitQueue, RabbitExchange
from faststream.rabbit.schemas.constants import ExchangeType
from pydantic import BaseModel

class RabbitMQConsumer:
    def __init__(
        self,
        dsn: str,
        exchange_name: str,
        routing_key: str,
        handler: Callable[[BaseModel], None],
    ):
        self._broker = RabbitBroker(dsn)
        self._app = FastStream(self._broker)
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._handler = handler
        self._setup_consumers()

    def _setup_consumers(self):
        """Setup all consumers from environment configuration"""

        # Main consumer
        queue_name = f'{self._exchange_name}_{self._routing_key.replace(".*.","_").replace(".*", "")}'

        self._create_consumer(
            queue_name=queue_name,
            routing_key=self._routing_key
        )

    def _create_consumer(
        self, 
        queue_name: str, 
        routing_key: str, 
    ):
        """Create a consumer without decorators"""
        print("Creating consumer", queue_name, routing_key)
        exchange = RabbitExchange(name=self._exchange_name, type=ExchangeType.TOPIC, durable=True)
        queue = RabbitQueue(name=queue_name, routing_key=routing_key, durable=True)
        subscriber = self._broker.subscriber(
            queue=queue, exchange=exchange
        )
        subscriber(self._handler)

    async def run(self):
        """Run the consumer"""
        logger = Logger('RabbitMQConsumer')
        logger.info("Starting RabbitMQ consumer...")
        await self._app.run()
