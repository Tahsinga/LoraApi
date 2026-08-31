from django.urls import path
from .views import branch_sync, health_check, main_sync, index, favicon

urlpatterns = [
    path('', index, name='index'),
    path('health/', health_check, name='health_check'),
    path('branch-sync/', branch_sync, name='branch_sync'),
    path('main-sync/', main_sync, name='main_sync'),
]
