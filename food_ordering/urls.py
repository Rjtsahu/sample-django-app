from django.urls import path, include
from django.conf.urls import url
from food_ordering import views
from food_ordering.consumers import WsConsumer

urlpatterns = [
    path('', views.home),
    path('task/', views.task),
    path('task/<int:task_id>', views.task),
    path('task/latest', views.latest_agent_task_view),
    path('logout', views.do_logout),
    path('accounts/', include('django.contrib.auth.urls'))
]


websocket_urlpatterns = [
    url(r'^ws/(?P<room_name>[^/]+)/$', WsConsumer),
]
