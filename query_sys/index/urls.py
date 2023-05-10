from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index_view, name='index'),
    path('result/', views.Result_view, name='result'),
]
