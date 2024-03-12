from django.urls import path
from .views import index, about, contact, process_route

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('process_route/', process_route, name='process_route')
]