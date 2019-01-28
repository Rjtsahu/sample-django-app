"""
A file to handle business logic associated to a view
"""
from food_ordering.models import Task, TaskTransaction, AssignedTask
from datetime import datetime
from food_ordering.constants import TaskStateConstant
from django.dispatch import receiver
from food_ordering.signals import ws_connected, ws_disconnected, ws_message
from food_ordering.consumers import WsConsumer
from food_ordering.queues import RedisQueue
import json


class TaskService(object):

    def __init__(self, req):
        self.request = req

    def __save__(self, data):
        task_obj = Task()
        task_obj.title = data['title']
        task_obj.description = data['description']
        task_obj.priority = data['priority']
        task_obj.created_by = self.request.user.id
        task_obj.last_modified_by = self.request.user.id
        task_obj.last_updated_at = datetime.utcnow()
        task_obj.save()

        task_trans_obj = TaskTransaction()
        task_trans_obj.task = task_obj
        task_trans_obj.updated_by = self.request.user
        task_trans_obj.save()
        return task_obj.id

    def save_task(self):
        """
        save a task to db and redis queue with sending proper notifications.
        :return: true or false based on success status
        """
        if self.request is None or self.request.POST is None:
            return False
        form_data = self.request.POST

        data = {'title': form_data.get('title', ''), 'description': form_data.get('detail', ''),
                'priority': form_data.get('priority', '1')}

        if data['title'] == '':
            return False

        task_id = self.__save__(data)

        # push this item into redis queue
        redis_queue = RedisQueue()

        task_obj = Task.objects.get(pk=task_id)

        NotificationService.notify_new_task_available(task_obj)
        redis_queue.add_item(RedisQueue.to_json_str(task_obj), task_obj.priority)

        return True

    def __update_task_state__(self, task_id, task_state):
        """
        Updates a given task as task_state_id
        :return:
        """
        task_obj = Task.objects.get(pk=task_id)
        task_obj.current_task_state = task_state
        task_obj.last_modified_by = self.request.user.id
        task_obj.last_updated_at = datetime.utcnow()
        task_obj.save()

        task_trans_obj = TaskTransaction()
        task_trans_obj.task = task_obj
        task_trans_obj.action_taken = task_state
        task_trans_obj.updated_at = datetime.utcnow()
        task_trans_obj.updated_by = self.request.user
        task_trans_obj.save()

    @staticmethod
    def _update_task_assigned_state(task_id, is_completed=False, is_declined=False):
        assigned_task_obj = AssignedTask.objects.get(task_id=task_id)
        assigned_task_obj.is_completed = is_completed
        assigned_task_obj.is_declined = is_declined
        assigned_task_obj.save()

    def cancel_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.CANCELLED)

    def accept_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.ACCEPTED)

    def complete_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.COMPLETED)
        self._update_task_assigned_state(task_id, is_completed=True)

    def decline_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.DECLINED)
        self._update_task_assigned_state(task_id, is_declined=True)


class AssignedTaskService:
    """
    This service holds method related to agent
    """

    def __init__(self, req):
        self.request = req

    def get_task_list(self):
        """
        Returns list of associated task to a user which are not cancelled or started.
        :return: Task list
        """
        assigned_tasks = AssignedTask.objects.filter(assign_to=self.request.user). \
            filter(is_completed=False).filter(is_declined=False)
        tasks = []
        for assigned_task in assigned_tasks:
            current_task_state = assigned_task.task.current_task_state
            if current_task_state == TaskStateConstant.ACCEPTED:
                tasks.append(assigned_task.task)

        return tasks


class WebSocketSignalHandlerService(object):

    def __init__(self):
        pass

    @staticmethod
    @receiver(ws_message)
    def on_ws_message(sender, **kwargs):
        print('signal on_ws_message: ', kwargs)

    @staticmethod
    @receiver(ws_connected)
    def on_ws_connected(sender, **kwargs):
        print('signal on_ws_connected, clientId: ', kwargs)

    @staticmethod
    @receiver(ws_disconnected)
    def on_ws_disconnected(sender, **kwargs):
        print('signal on_ws_disconnected, clientId: ', kwargs)


class NotificationService(object):

    def __init__(self, req):
        self.request = req
        self.redis_queue = RedisQueue()

    def notify_task_completed(self, task_id):
        self._notify_task_state_changed(task_id, 'completed')

    def notify_task_cancelled(self, task_id):
        self._notify_task_state_changed(task_id, 'cancelled')

    def notify_task_accepted(self, task_id):
        self._notify_task_state_changed(task_id, 'accepted')

        # notify agents about next high priority task
        # Its better send notification data from ws only,
        # this will prevent multiple redis call if perform
        # api refresh on this notification

        top_task = self.get_task_to_display()
        if top_task is not None:
            message = {
                'event': 'new-task-request',
                'data': top_task,
            }
            WsConsumer.group_send(json.dumps(message), WsConsumer.agent_group)

    def notify_task_declined(self, task_id):
        self._notify_task_state_changed(task_id, 'declined')

    def _notify_task_state_changed(self, task_id, task_state):
        task = Task.objects.get(pk=task_id)
        task_state = str(task_state).lower()
        message = {
            'event': 'task-{0}'.format(task_state),
            'data': 'One of task has been {0} .'.format(task_state),
            'sender': self.request.user.full_name,
            'taskTitle': task.title
        }

        WsConsumer.group_send(json.dumps(message), WsConsumer.manager_group)

    @staticmethod
    def notify_new_task_available(task_obj):
        """
        To be notified only if existing queue was empty.
        This notification will be sent to all agents
        :return:
        """
        redis_queue = RedisQueue()
        if redis_queue.get_top_priority_item() is None:
            message = {
                'event': 'new-task-request',
                'data': RedisQueue.to_py_dict(RedisQueue.to_json_str(task_obj)),
            }
            WsConsumer.group_send(json.dumps(message), WsConsumer.agent_group)

    def get_task_to_display(self):
        """
        This method will get top priority task,it will keep popping
        tasks if its state has been changes to cancel.
        :return: task with highest priority
        """
        while True:
            top_task = RedisQueue.to_py_dict(self.redis_queue.get_top_priority_item())
            if top_task is None:
                break

            task_obj = Task.objects.get(pk=top_task['id'])

            if task_obj.current_task_state == TaskStateConstant.NEW:
                # this is a valid task
                break
            else:
                # pop this task as its already cancelled
                if self.redis_queue.get_top_priority_item(RedisQueue.to_json_str(top_task)) is None:
                    # this is uncommon scenario, can happen when other thread win before this.
                    break
        return top_task
