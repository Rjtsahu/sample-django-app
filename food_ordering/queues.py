"""
This file will handle rabbit mq relate producer consumer
problem over prioritized queues
"""

import pika


class RabbitMqHandler(object):
    queue_name_prefix = 'task_queue_'
    parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/')
    message_property = pika.BasicProperties(content_type='text/plain', delivery_mode=1)

    def __init__(self):
        self.connection = pika.BlockingConnection(parameters=RabbitMqHandler.parameters)
        self.channel = self.connection.channel()

    def send_message(self):
        self.channel.basic_publish('test_exchange',
                                   'test_routing_key',
                                   'message body value',
                                   RabbitMqHandler.message_property
                                   )

    def get_message(self, queue_name):
        self.channel.basic_get(queue_name)

    def __stop__(self):
        self.connection.close()


