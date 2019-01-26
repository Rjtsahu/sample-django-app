from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from food_ordering.services import TaskService, AssignedTaskService, NotificationService
from food_ordering.models import Task, CustomUser, TaskTransaction

LOGIN_URL = '/accounts/login'


def test(request):
    return HttpResponse('Server is Up')


@login_required(login_url=LOGIN_URL)
def home(req):
    if req.user.get_user_type() == 'Manager':
        return manager_home_view(req)
    elif req.user.get_user_type() == 'DeliveryAgent':
        return delivery_agent_home_view(req)
    else:
        return redirect('/accounts/login')


def manager_home_view(req):
    context = {'user': req.user}
    return render(req, 'manager/home.html', context)


def delivery_agent_home_view(req):
    context = {'user': req.user}
    # TODO: add logic to send list of tasks
    return render(req, 'agent/home.html', context)


@login_required(login_url=LOGIN_URL)
def task(req, task_id=None):
    if req.user.get_user_type() == 'Manager':
        return task_manager_view(req, task_id)
    elif req.user.get_user_type() == 'DeliveryAgent':
        return task_agent_view(req, task_id)
    else:
        return redirect('/accounts/login')


def task_manager_view(req, task_id):
    task_service = TaskService(req)
    notification_service = NotificationService(req)

    if req.method == 'POST' and task_id is None:
        # save form data
        task_service.save_task()
        return redirect('/')
    elif req.method == 'GET' and task_id is None:
        tasks = Task.objects.all()
        return render(req, 'manager/task-list.html', {'tasks': tasks})
    elif req.method == 'GET' and task_id is not None:
        # show task transition page
        task_obj = get_object_or_404(Task, pk=task_id)
        creator = CustomUser.objects.get(pk=task_obj.created_by)
        transaction = TaskTransaction.objects.filter(task_id=task_id).order_by('-updated_at')

        context = {'task': task_obj, 'creator_username': creator.username, 'transaction': transaction}
        return render(req, 'manager/task.html', context)
    elif req.method == 'DELETE' and task_id is not None:
        task_service.cancel_task(task_id)
        # send proper notifications
        notification_service.notify_task_cancelled(task_id)
        return HttpResponse('ok')
    else:
        return redirect('/')


def task_agent_view(req, task_id):
    assigned_task_service = AssignedTaskService(req)
    task_service = TaskService(req)
    notification_service = NotificationService(req)

    context = {}
    if req.method == 'GET':
        tasks = assigned_task_service.get_task_list()
        context['tasks'] = tasks
        return render(req, 'agent/task.html', context)
    elif req.method == 'PUT':
        '''
        PUT should be used for performing COMPLETE,DELCINE and ACCEPT operations
        '''
        action = req.GET['action']
        if action == 'accepted':
            task_service.accept_task(task_id)
            notification_service.notify_task_accepted(task_id)
        elif action == 'completed':
            task_service.complete_task(task_id)
            notification_service.notify_task_completed(task_id)
        elif action == 'declined':
            task_service.decline_task(task_id)
            notification_service.notify_task_declined(task_id)
        else:
            return HttpResponse('Invalid action name.')
        return HttpResponse('ok')
    else:
        return redirect('/')
