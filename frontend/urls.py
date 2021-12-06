from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.login),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout),
    path('', views.index, name='index'),
    path('api/kill_target', views.kill),
    path('api/kill_target/confirm', views.kill_confirm),
    path('api/kill_target/cancel', views.kill_cancel),

]
