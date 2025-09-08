import logging

from kombu import Connection, Exchange, Producer

from twingly_pyamqp.amqp_config import AMQPconfig
from twingly_pyamqp.constants import DEFAULT_EXCHANGE_OPTS


class Publisher:
    def __init__(
        self,
        exchange_name: str | None = None,
        routing_key: str | None = None,
        config: AMQPconfig = None,
        exchange_opts: dict | None = None,
        max_retries: int | None = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.config = config or AMQPconfig()
        self.connection = Connection(self.config.connection_urls())
        self.exchange = Exchange(
            exchange_name or "", **(exchange_opts or DEFAULT_EXCHANGE_OPTS)
        )
        self.routing_key = routing_key
        self.max_retries = max_retries

    def publish(
        self,
        payload: object,
        routing_key: str | None = None,
        publish_args: dict | None = None,
    ):
        key = routing_key or self.routing_key

        producer = Producer(self.connection)
        publish = self.connection.ensure(
            producer,
            producer.publish,
            errback=self.on_connection_error,
            max_retries=self.max_retries,
        )
        publish(
            payload,
            exchange=self.exchange,
            routing_key=key,
            **(publish_args or {}),
        )

    def on_connection_error(self, exc: Exception, _):
        self.logger.error(f"Connection error occurred: {exc}")
