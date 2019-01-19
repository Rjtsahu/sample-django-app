from django.shortcuts import render
from django.http import HttpResponse


def test(request):
    return HttpResponse('Server is Up')


def index(req):
    return render(req, 'index.html')


# to be handled if user is already logged in
def home(req):
    print(req.user.get_user_type())
    context = {'user': req.user}
    return render(req, 'index.html',context)
