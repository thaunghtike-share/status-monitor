from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.status_overview, name='status-overview'),
]