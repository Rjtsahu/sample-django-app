from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from food_ordering.services import TaskService
from food_ordering.models import Task, CustomUser, TaskTransaction


def test(request):
    return HttpResponse('Server is Up')


def home(req):
    if req.user.is_authenticated:
        if req.user.get_user_type() == 'Manager':
            return manager_home_view(req)
        elif req.user.get_user_type() == 'DeliveryAgent':
            return delivery_agent_home_view(req)
        else:
            return redirect('/accounts/login')
    else:
        return redirect('/accounts/login')


def manager_home_view(req):
    tasks = Task.objects.all()

    context = {'user': req.user, 'tasks': tasks}
    return render(req, 'manager/home.html', context)


def delivery_agent_home_view(req):
    context = {'user': req.user}
    # TODO: add logic to send list of tasks
    return render(req, 'agent/home.html', context)


def task(req, task_id=None):
    if req.user.is_authenticated:
        if req.user.get_user_type() == 'Manager':
            return task_manager_view(req, task_id)
        elif req.user.get_user_type() == 'DeliveryAgent':
            return task_agent_view(req, task_id)
        else:
            return redirect('/accounts/login')
    else:
        return redirect('/accounts/login')


def task_manager_view(req, task_id):
    task_service = TaskService(req)

    if req.method == 'POST' and task_id is None:
        # save form data
        task_service.save_task()
        return redirect('/')
    elif req.method == 'GET' and task_id is not None:
        # show task transition page
        task = get_object_or_404(Task, pk=task_id)
        creator = CustomUser.objects.get(pk=task.created_by)
        transaction = TaskTransaction.objects.filter(task_id=task_id).order_by('-updated_at')

        context = {'task': task, 'creator_username': creator.username, 'transaction': transaction}
        return render(req, 'manager/task.html', context)
    elif req.method == 'DELETE' and task_id is not None:
        task_service.cancel_task(task_id)
        return HttpResponse('ok')
    else:
        return redirect('/')


def task_agent_view(req):
    if req.method == 'GET':
        delivery_agent_tasks = Task.objects.filter(assigned_to=req.user). \
            values_list('task', flat=True)
        context = {'task': delivery_agent_tasks}
        return render(req, 'agent/task.html',context)
    else:
        return redirect('/')
