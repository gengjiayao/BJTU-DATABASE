from django.urls import path
from . import views

urlpatterns = [
    path('', views.toLogin_view),
    path('login/', views.Login_view),
    path('forgot/', views.Forget_view),
    path('register/', views.toRegister_view),
    path('send_code/', views.Get_Code),
    path('login/register/', views.Register_view),
]
