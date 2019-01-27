import redis
from food_ordering.utils import get_env_variable

"""
This file will handle producer consumer
problem over prioritized queues using redis
"""
"""
This class will primarily handle 3 tasks
1) add a given task with given priority in redis queue
2) get the task with highest priority and queue order
3) maintain current top task's instance
"""


class RedisQueue(object):
    queue_prefix = 'task_'
    priorities = [1, 2, 3]  # 1 denoting high and 3 low

    def __init__(self, uri=None):
        self.connection_property = self.get_connection_detail_from_redis_uri(
            get_env_variable('REDIS_CONNECTION') if uri is None else uri)

        self.redis_client = redis.Redis(
            host=self.connection_property['host'],
            port=self.connection_property['port'],
            password=self.connection_property['password'] if 'password' in self.connection_property else None)

    def add_item(self, item, priority=1):
        if priority not in RedisQueue.priorities:
            raise ValueError('Invalid value for priority')
        self.redis_client.lpush('lisrt', item)

    @staticmethod
    def get_connection_detail_from_redis_uri(uri):
        detail = {}
        if type(uri) is not str:
            raise TypeError('uri must be string.')
        if not uri.startswith('redis://'):
            raise ValueError('given string is not proper redis uri.')
        uri = uri.split('redis://')[1]
        if '@' in uri:
            detail['password'] = uri.split('@')[0].split(':')[1]
            detail['host'] = uri.split('@')[1].split(':')[0]
            detail['port'] = uri.split('@')[1].split(':')[1]
        else:
            detail['host'] = uri.split(':')[0]
            detail['port'] = uri.split(':')[1]
        return detail

    @staticmethod
    def get_priority_queue_name(priority=1):
        return RedisQueue.queue_prefix + str(priority)
