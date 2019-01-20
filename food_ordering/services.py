"""
A file to handle business logic associated to a view
"""
from food_ordering.models import Task, TaskTransaction
from datetime import datetime


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
