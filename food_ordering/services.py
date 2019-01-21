"""
A file to handle business logic associated to a view
"""
from food_ordering.models import Task, TaskTransaction, AssignedTask
from datetime import datetime
from food_ordering.constants import TaskStateConstant, TaskPriorityConstant


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

    def save_task(self):
        """
        save a task to db
        :param form_data: input POST data from HTTP request
        :return: true or false based on success status
        """
        if self.request is None or self.request.POST is None:
            return False
        form_data = self.request.POST

        data = {'title': form_data.get('title', ''), 'description': form_data.get('detail', ''),
                'priority': form_data.get('priority', '')}

        if data['title'] == '':
            return False

        self.__save__(data)
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

    def cancel_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.CANCELLED)

    def accept_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.ACCEPTED)

    def complete_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.COMPLETED)

    def decline_task(self, task_id):
        self.__update_task_state__(task_id, TaskStateConstant.DECLINED)


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
        assigned_tasks = AssignedTask.objects.filter(assign_to=self.request.user)
        tasks = []
        for assigned_task in assigned_tasks:
            current_task_state = assigned_task.task.get_current_task_state_type()
            if current_task_state not in ['NEW', 'CANCELLED']:
                tasks.append(assigned_task.task)

        return tasks
