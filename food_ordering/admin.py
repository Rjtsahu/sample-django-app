from django.contrib import admin
from .models import CustomUser,AssignedTask,Task,TaskTransaction

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Task)
admin.site.register(AssignedTask)
admin.site.register(TaskTransaction)