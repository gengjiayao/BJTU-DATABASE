import time
import threading
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
from datetime import datetime, timedelta
from jinja2 import Template
import hashlib
import json
import pytz

lock = threading.Lock()


def atomic(func):
    def wrap(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return wrap


# Create your views here.
def Index_view(request):
    return render(request, 'index.html')


@atomic
def Result_view(request):
    time.sleep(1)
    current_user = request.POST.get('current_user', '')
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

    sql = "insert into query_info(user_account, query_start, query_end) values(%s, %s, %s) "
    params = (current_user, from_city, to_city)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)

    sql = "call get_transfer_data(%s, %s)"
    params = (from_city, to_city)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        results = cursor.fetchall()

    trains = []  # 结果列表
    for row in results:
        # 对每条结果数据建立字典
        train = {
            "trainNo": row[2],
            "startStation": row[0],
            "endStation": row[1],
        }
        trains.append(train)

    column0, column1, column2 = [], [], []
    for result in results:
        column0.append(result[0])
        column1.append(result[1])
        column2.append(result[2])

    arr_total0 = []
    for i, j, k in zip(column2, column0, column1):
        with connection.cursor() as cursor:
            cursor.execute("call get_min_total0(%s, %s, %s, %s);", (i, j, k, int(date_diff)))
            total0 = cursor.fetchall()[0][0]
            arr_total0.append(total0)
    for i in range(len(trains)):
        trains[i]['total0'] = arr_total0[i]

    arr_total1 = []
    for i, j, k in zip(column2, column0, column1):
        with connection.cursor() as cursor:
            cursor.execute("call get_min_total1(%s, %s, %s, %s);", (i, j, k, int(date_diff)))
            total1 = cursor.fetchall()[0][0]
            arr_total1.append(total1)
    for i in range(len(trains)):
        trains[i]['total1'] = arr_total1[i]

    arr_total2 = []
    for i, j, k in zip(column2, column0, column1):
        with connection.cursor() as cursor:
            cursor.execute("call get_min_total2(%s, %s, %s, %s);", (i, j, k, int(date_diff)))
            total2 = cursor.fetchall()[0][0]
            arr_total2.append(total2)
    for i in range(len(trains)):
        trains[i]['total2'] = arr_total2[i]
    return render(request, 'result.html', {'trains': trains})
