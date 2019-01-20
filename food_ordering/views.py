from django.shortcuts import render, redirect
from django.http import HttpResponse
from food_ordering.services import TaskService


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
    context = {'user': req.user}
    # TODO: add logic to send list of tasks
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
    if req.method == 'POST' and task_id is None:
        # save form data
        task_service = TaskService(req)
        task_service.save_task()
    return redirect('/')


def task_agent_view(req, task_id):
    pass
