from django.urls import path
from .views import home, DashboardVendasView

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', DashboardVendasView.as_view(), name='dashboard_vendas'),
]