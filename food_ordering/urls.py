from django.urls import path,include

from . import views

urlpatterns = [
    path('',views.home),
    path('task/', views.task),
    path('task/<int:task_id>',views.task),
    path('test', views.test),
    path('accounts/',include('django.contrib.auth.urls'))
]