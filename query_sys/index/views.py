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


def User_ch_pwd(request):
    pre_password = request.POST.get('pre_password', '')
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')

    u = request.session.get('username')
    print(pre_password, password, confirm_password)

    hash_p = hashlib.sha256(pre_password.encode()).hexdigest()

    cursor = connection.cursor()
    cursor.execute("select user_password from user where user_account ='{}';".format(u))
    row = cursor.fetchone()
    db_password = row[0]

    cursor.execute("select * from user_info_view where user_account = %s;", u)
    results = cursor.fetchall()
    username, id_number, phone = results[0][0], results[0][1], results[0][2]

    if db_password == hash_p:
        if password != confirm_password:
            context = {
                'user_msg': '前后密码不一致',
                'username': username,
                'id_number': id_number,
                'phone': phone,
            }
            return render(request, 'user.html', context)
        else:
            hash_p = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("update user set user_password = '{}' where user_account = '{}';".format(hash_p, u))
            context = {
                'user_msg_suss': '密码修改成功',
                'username': username,
                'id_number': id_number,
                'phone': phone,
            }
            return render(request, 'user.html', context)
    else:
        context = {
            'user_msg': '原密码错误',
            'username': username,
            'id_number': id_number,
            'phone': phone,
        }
        return render(request, 'user.html', context)


def User_info(request):
    u = request.session.get('username')
    if u:
        with connection.cursor() as cursor:
            cursor.execute("select * from user_info_view where user_account = %s;", u)
            results = cursor.fetchall()
            username, id_number, phone = results[0][0], results[0][1], results[0][2]
            context = {
                'username': username,
                'id_number': id_number,
                'phone': phone
            }
        return render(request, 'user.html', context)
    else:
        return redirect('/index')


@atomic
def Result_view(request):
    time.sleep(1)
    if not request.session.get('username'):
        return redirect('/index')

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
