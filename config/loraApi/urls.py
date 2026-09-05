from django.urls import path
from .views import (
    branch_status, branch_sync, cancel_sale, health_check, main_sync,
    index, favicon, confirm_deletion, cancellation_history,
    cancellation_history_api,
)

urlpatterns = [
    path('', index, name='index'),
    path('history/', cancellation_history, name='cancellation_history'),
    path('health/', health_check, name='health_check'),
    path('cancel-sale/', cancel_sale, name='cancel_sale'),
    path('branches/', branch_status, name='branch_status'),
    path('branch-sync/', branch_sync, name='branch_sync'),
    path('main-sync/', main_sync, name='main_sync'),
    path('confirm-deletion/', confirm_deletion, name='confirm_deletion'),
    path('cancellation-history/', cancellation_history_api, name='cancellation_history_api'),
]
