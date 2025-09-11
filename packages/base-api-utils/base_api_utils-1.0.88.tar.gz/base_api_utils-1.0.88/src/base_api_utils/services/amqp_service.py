import json
import logging
from typing import Any

import pika
from ..domain import DomainEvent
from ..utils import config

from . import AbstractEventDispatcher
from .abstract_domain_events_service import AbstractDomainEventsService
from ..domain import EventMessage


class AMQPService(AbstractDomainEventsService):
    def __init__(self,
                 event_dispatcher: AbstractEventDispatcher,
                 rabbit_host=config('RABBIT.HOST'),
                 rabbit_port=config('RABBIT.PORT'),
                 rabbit_username=config('RABBIT.USER'),
                 rabbit_password=config('RABBIT.PASSWORD'),
                 exchange_name=config('RABBIT.EXCHANGE'),
                 queue_name=config('RABBIT.QUEUE'),
                 routing_keys=None):

        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.credentials = pika.PlainCredentials(rabbit_username, rabbit_password)

        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.routing_keys = routing_keys or []
        self.connection = None
        self.channel = None

        self.dispatcher = event_dispatcher

    def _is_valid_event(self, event_type: str) -> bool:
        try:
            return any(routing_key == event_type for routing_key in self.routing_keys)
        except:
            return False

    def _connect(self):
        """Establish connection and declare exchange/queue."""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host,
                                                                            port=self.rabbit_port,
                                                                            credentials=self.credentials))
        self.channel = self.connection.channel()

        # Declare a direct exchange
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="direct")

        # Declare a durable queue
        self.channel.queue_declare(queue=self.queue_name, durable=True)

        # Bind queue to all provided routing keys
        for key in self.routing_keys:
            self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=key)
            logging.getLogger('api').info(f"Queue {self.queue_name} bound to {key}")

    def _callback(self, ch, method, properties, body):
        """Process incoming messages depending on routing key."""
        logging.getLogger('api').info(f"Message received: {body} with routing_key={method.routing_key}")

        try:
            event = EventMessage.from_rabbit(ch, method, properties, body)

            # Validate it's a known event
            if not self._is_valid_event(event.event_type):
                logging.getLogger('api').warning(f"Unknown event type: {event.event_type}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Process event
            success = self.dispatcher.dispatch(event)

            if success:
                # Accept
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Reject
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except Exception as e:
            logging.getLogger('api').error(f"Critical error processing message: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def publish(self, message: Any, event_type: DomainEvent, exchange: str = None):
        rabbit_exchange = exchange if not exchange is None else config('RABBIT.EXCHANGE')
        rabbit_default_routing_key = event_type if not event_type is None else config('RABBIT.DEFAULT_ROUTING_KEY')

        cnn = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_host,
                                                                port=self.rabbit_port,
                                                                credentials=self.credentials))
        channel = cnn.channel()
        channel.exchange_declare(exchange=rabbit_exchange, exchange_type='direct', durable=True)

        message_body = json.dumps(message).encode('utf-8')

        channel.basic_publish(
            exchange=rabbit_exchange,
            routing_key=rabbit_default_routing_key,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent message
            ),
        )
        cnn.close()

        (logging.getLogger('api')
         .debug(f'Message sent to exchange {rabbit_exchange} using routing_key {rabbit_default_routing_key}'))

    def subscribe(self):
        """Start listening messages from the queue."""
        if not self.channel:
            self._connect()

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._callback
        )

        logging.getLogger('api').info("Waiting for messages...")
        self.channel.start_consuming()