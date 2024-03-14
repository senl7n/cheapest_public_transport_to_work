from django.urls import path

from .views import index, process_route

urlpatterns = [
    path('', index, name='index'),
    path('process_route/', process_route, name='process_route')
]
