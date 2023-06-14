from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index_view, name='index'),
    path('user/', views.User_info, name='user_info'),
    path('result/', views.Result_view, name='result'),
    path('user/ch_pwd/', views.User_ch_pwd, name='ch_pwd')
]
