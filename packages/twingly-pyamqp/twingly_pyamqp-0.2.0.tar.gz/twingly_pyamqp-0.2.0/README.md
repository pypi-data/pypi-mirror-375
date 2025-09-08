# Twingly::PYAMQP

[![GitHub Build Status](https://github.com/twingly/twingly-amqp/workflows/CI/badge.svg)](https://github.com/twingly/twingly-amqp/actions)

A Python implementation of the [twingly-amqp gem](https://github.com/twingly/twingly-amqp) for subscribing and publishing messages via RabbitMQ.

## Usage

Environment variables:

- `RABBITMQ_N_HOST` - Defaults to `localhost`
- `AMQP_USERNAME` - Defaults to `guest`
- `AMQP_PASSWORD` - Defaults to `guest`

## Docs

### AMQPconfig

Used to configure `RabbitMQ` host, port, user, and password. Arguments take precedence over environment variables and should only be used to override environment or default values, since env variables and default values are used if no AMQPconfig is provided.

Arguments

- rabbitmq_host
- rabbitmq_port
- amqp_user
- amqp_password

### AMQP Connection

Exchange options match Kombu Exchange Arguments, similarly, queue options match those defined in Kombu Queue Arguments.

#### Arguments

##### Constructor

| Argument | Type                 | Default | Description                                                                                   |
| -------- | -------------------- | ------- | --------------------------------------------------------------------------------------------- |
| `config` | `AMQPconfig \| None` | `None`  | Optional AMQPconfig to override RabbitMQ connection. Defaults to using environment variables. |

#### Methods

###### declare_queue

| Argument        | Type           | Default | Description                                                                           |
| --------------- | -------------- | ------- | ------------------------------------------------------------------------------------- |
| `queue_name`    | `str`          | No      | The name of the queue to declare.                                                     |
| `exchange_name` | `str \| None`  | `None`  | The name of the exchange the queue is bound to. If `None`, uses the default exchange. |
| `routing_key`   | `str \| None`  | `None`  | The routing key for the queue. If `None`, defaults to `queue_name`.                   |
| `exchange_opts` | `dict \| None` | `None`  | Optional dictionary of options to configure the exchange.                             |
| `queue_opts`    | `dict \| None` | `None`  | Optional dictionary of options to configure the queue.                                |

Raises `ValueError` if a routing key is set without specifying an exchange.

###### declare_exchange

| Argument        | Type           | Default | Description                                      |
| --------------- | -------------- | ------- | ------------------------------------------------ |
| `exchange_name` | `str`          | No      | The name of the exchange to declare.             |
| `exchange_opts` | `dict \| None` | `None`  | Optional dictionary of options for the exchange. |

#### Example Usage

```python
# Establish an AMQP connection
connection = AmqpConnection()

# Declare an exchange
connection.declare_exchange("logs")

# Declare an exchange with optional options
connection.declare_exchange("logs", exchange_opts={"type": "topic", "durable": False})

# Declare a queue on default exchange
connection.declare_queue(queue_name="task_queue")

# Declare a queue and bind to exchange and routing key
connection.declare_queue(
    queue_name="task_queue",
    exchange_name="logs",
    routing_key="task_key",
    queue_opts={"max_length": 1000}
)
```

---

### Publisher

#### Arguments

##### Constructor

| Argument        | Type                 | Default | Description                                                                                    |
| --------------- | -------------------- | ------- | ---------------------------------------------------------------------------------------------- |
| `exchange_name` | `str \| None`        | `None`  | The name of the exchange to route the messages to. Leave empty to publish to default exchange. |
| `routing_key`   | `str \| None`        | `None`  | The routing key used for directing the message.                                                |
| `config`        | `AMQPconfig \| None` | `None`  | Optional override configuration for AMQP connection settings.                                  |
| `publish_args`  | `dict \| None`       | `None`  | Additional arguments that match the publish method arguments of Kombu's Producer.              |

##### Methods

###### publish

| Argument      | Type          | Default | Description                                  |
| ------------- | ------------- | ------- | -------------------------------------------- |
| `payload`     | `object`      | No      | The message to publish to the exchange.      |
| `routing_key` | `str \| None` | `None`  | Optionally override the default routing key. |

Raises `ValueError` if no routing key is provided at instantiation or publication time.

#### Example Usage

```python
# Create an instance of Publisher with default values
publisher = Publisher()

# Create an instance of Publisher with a specific routing key
publisher = Publisher(exchange_name="custom_exchange", routing_key="custom_routing_key")

# Publish messages
publisher.publish({"message": "hello, RabbitMQ"})  # Uses the routing key specified at instantiation
publisher.publish({"message": "hello, RabbitMQ"}, routing_key="override_routing_key") # Overrides routing key

# Publish message with additional arguments
publisher.publish({"message": "hello, RabbitMQ"}, publish_args={"priority": 7})
```

---

### Subscription

#### Arguments

##### Constructor

| Argument      | Type                 | Default | Description                                                                |
| ------------- | -------------------- | ------- | -------------------------------------------------------------------------- |
| `queue_names` | `str \| list[str]`   | No      | The name of the queue(s) to subscribe to. Accepts a single name or a list. |
| `config`      | `AMQPconfig \| None` | `None`  | Optional override configuration for AMQP connection settings.              |

##### Methods

###### subscribe

| Argument              | Type                                                                   | Default | Description                                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `callbacks`           | `Callable[[str, object], None] \| list[Callable[[str, object], None]]` | No      | The function(s) to process incoming messages.                                                                                                                                               |
| `blocking`            | `bool`                                                                 | `True`  | If `True`, blocks the main thread while consuming messages.                                                                                                                                 |
| `timeout`             | `int \| None`                                                          | `None`  | Maximum time (in seconds) to wait for messages. Required if `blocking=False`.                                                                                                               |
| `max_connect_attempt` | `int`                                                                  | `3`     | Maximum number of retries for establishing a connection.                                                                                                                                    |
| `consumer_args`       | `dict \| None`                                                         | `None`  | Additional arguments that match [Kombu's Consumer](https://docs.celeryq.dev/projects/kombu/en/stable/userguide/consumers.html#:~:text=Message%20consumer.-,Arguments,-%3A%C2%B6) arguments. |

Raises `ValueError` if `blocking=False` and no `timeout` is provided.
Raises `ValueError` if a subscription is already active.

###### cancel

| Argument | Type | Default | Description                                                   |
| -------- | ---- | ------- | ------------------------------------------------------------- |
| None     | -    | -       | Cancels the active subscription and stops consuming messages. |

#### Example Usage

```python
# Create an instance of Subscription for a single queue
subscription = Subscription(queue_names="task_queue")

# Create an instance of Subscription for multiple queues
subscription = Subscription(queue_names=["queue1", "queue2"])

# Subscribe to messages in blocking mode
subscription.subscribe(callback=Callable[[str, object], None])

# Subscribe to messages in non-blocking mode with a timeout
subscription.subscribe(callback=Callable[[str, object], None], blocking=False, timeout=5,consumer_args={"no_ack": True, "prefetch_count": 5})

# Cancel the subscription
subscription.cancel()
```
