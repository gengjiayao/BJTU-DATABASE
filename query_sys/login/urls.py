from django.urls import path
from . import views

urlpatterns = [
    path('', views.toLogin_view),
    path('login/', views.Login_view),
    path('forgot/', views.Forget_view),
    path('register/', views.Register_view),
]
