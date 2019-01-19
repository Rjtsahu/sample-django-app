from django.urls import path,include

from . import views

urlpatterns = [
    path('',views.home),
    path('test', views.test),
    path('index',views.index),
    path('accounts/',include('django.contrib.auth.urls'))
]