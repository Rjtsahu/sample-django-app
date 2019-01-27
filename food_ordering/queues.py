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
    current_item = 'current_task'

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
        self.redis_client.lpush(self.get_priority_queue_name(priority), item)
        if self.redis_client.get(RedisQueue.current_item) is None:
            self.redis_client.set(RedisQueue.current_item, item)

    def get_current_item(self):
        item = self.redis_client.get(RedisQueue.current_item)
        return item

    def pop_priority_item(self, current_item):
        """
        This will pop highest priority item and keeps it saved in current_item (redis).
        :current_item: Popping is valid if only current_item matches with current_item value in redis.
        :return: popped_item
        """
        popped_item = None

        if current_item != self.get_current_item():
            return popped_item

        for _priority in sorted(RedisQueue.priorities):
            if self.redis_client.llen(self.get_priority_queue_name(_priority)) == 0:
                continue
            else:
                popped_item = self.redis_client.rpop(self.get_priority_queue_name(_priority))
                break

        return popped_item

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
