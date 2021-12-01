from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.login),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout),
    path('', views.index, name='index'),
]
