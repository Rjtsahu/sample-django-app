import json
import redis
import threading
from food_ordering.utils import get_env_variable, to_utf

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
    _lock = threading.Lock()

    def __init__(self, uri=None):
        self.connection_property = self.get_connection_detail_from_redis_uri(
            get_env_variable('REDIS_CONNECTION') if uri is None else uri)

        self.redis_client = redis.Redis(
            host=self.connection_property['host'],
            port=self.connection_property['port'],
            password=self.connection_property['password'] if 'password' in self.connection_property else None)

    def add_item(self, item, priority=priorities[0]):
        if priority not in RedisQueue.priorities:
            raise ValueError('Invalid value for priority')
        self.redis_client.lpush(self.get_priority_queue_name(priority), item)

    def get_top_priority_item(self, pop_only_when_item=None):
        """
        This method will gets the item at top priority in redis queues,
        This method will re-push last popped item to queue head if :param pop_only_when_item matched popped item.
        :param pop_only_when_item : item (string representation) which is assumed to be equal to popped data.
        :return: popped_item
        """
        popped_item = None

        for _priority in sorted(RedisQueue.priorities):
            queue_name = self.get_priority_queue_name(_priority)
            if self.redis_client.llen(queue_name) == 0:
                continue
            else:
                RedisQueue._lock.acquire()
                popped_item = self.redis_client.rpop(queue_name)

                if pop_only_when_item is None or to_utf(popped_item) != pop_only_when_item:
                    # push back item at head of queue
                    self.redis_client.rpush(queue_name, popped_item)
                else:
                    # don't push back again
                    pass

                RedisQueue._lock.release()

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

    @staticmethod
    def to_json_str(task_model_obj, is_django_model=True):
        if not is_django_model:
            # in case of python object
            return json.dumps(task_model_obj)
        task_obj = {'title': task_model_obj.title, 'id': task_model_obj.id,
                    'detail': task_model_obj.description, 'priority': task_model_obj.priority}
        return json.dumps(task_obj)

    @staticmethod
    def to_py_dict(task_str):
        if task_str is not None:
            return json.loads(to_utf(task_str))
