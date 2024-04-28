from django.contrib import admin
from django.urls import path
from myapp.views import login_view
from myapp.views import dashboard_view

urlpatterns = [
    path('', login_view.user_login, name='user_login'),
    path('dashboard/', dashboard_view.dashboard, name='dashboard'),
    path('logout/', login_view.logout_view),
    path('demo/', dashboard_view.demo, name='demo'),
]
