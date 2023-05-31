from django.urls import path
from . import views

urlpatterns = [
    path('', views.toLogin_view),
    path('login/', views.Login_view, name='login'),
    path('exit/', views.exit_view, name='exit'),
    path('forgot/', views.toForget_view),
    path('register/', views.toRegister_view),
    path('logout/', views.toLogout_view),
    path('send_code/', views.Get_Code),
    path('login/register/', views.Register_view),
    path('login/forgot/', views.Forget_view),
    path('login/logout/', views.Logout_view),
]
