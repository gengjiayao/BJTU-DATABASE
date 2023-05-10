from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
from datetime import datetime, timedelta
import hashlib
import json
import pytz


# Create your views here.
def Index_view(request):
    return render(request, 'index.html')


# def Result_view(request):
#     return render(request, 'result.html')


def Result_view(request):
    from_city = request.POST.get('start', '')
    to_city = request.POST.get('end', '')
    selected_date = request.POST.get('date')
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d')  # 转换为日期对象
    utc_tz = pytz.timezone('UTC')  # 设置时区为UTC
    utc_selected_date = utc_tz.localize(selected_date)  # 转换为UTC时间
    beijing_tz = pytz.timezone('Asia/Shanghai')  # 设置时区为北京时间
    beijing_selected_date = utc_selected_date.astimezone(beijing_tz)  # 将UTC时间转换为北京时间
    beijing_now = datetime.now(beijing_tz)  # 获取当前北京时间
    date_diff = (beijing_selected_date - beijing_now).days
    print(date_diff)

    return render(request, 'result.html')
