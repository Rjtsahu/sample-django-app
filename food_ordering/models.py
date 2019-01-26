from django.db import models
from django.contrib.auth.models import AbstractUser
from food_ordering.utils import get_option_value

# Create your models here.

USER_TYPE = (
    (1, 'Manager'),
    (2, 'DeliveryAgent')
)

PRIORITY = (
    (1, 'HIGH'),
    (2, 'MEDIUM'),
    (3, 'LOW')
)

TASK_STATE = (
    (1, 'NEW'),
    (2, 'ACCEPTED'),
    (3, 'COMPLETED'),
    (4, 'DECLINED'),
    (5, 'CANCELLED')
)


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    user_type = models.IntegerField(choices=USER_TYPE, default=1)

    def get_user_type(self):
        return get_option_value(USER_TYPE, self.user_type)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(default='')
    priority = models.IntegerField(
        choices=PRIORITY, default=1)
    created_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField()
    last_updated_at = models.DateTimeField()
    last_modified_by = models.IntegerField()
    current_task_state = models.IntegerField(
        choices=TASK_STATE, default=1)

    def get_priority_type(self):
        return get_option_value(PRIORITY, self.priority)

    def get_current_task_state_type(self):
        return get_option_value(TASK_STATE, self.current_task_state)


class AssignedTask(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='task')
    assign_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                  related_name='DeliveryAgent')
    assign_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)


class TaskTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    action_taken = models.IntegerField(choices=TASK_STATE, default=1)

    def get_action_taken_value(self):
        return get_option_value(TASK_STATE, self.action_taken)
