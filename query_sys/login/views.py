from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
import hashlib
import json


# Create your views here.
def toLogin_view(request):
    return render(request, 'login.html')


def toRegister_view(request):
    return render(request, 'register.html')


Code = None


def Get_Code(request):
    global Code
    if request.method == 'POST':
        json_data = json.loads(request.body)
        Code = json_data.get('Code', '123')
        print("6位验证码：" + Code)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "message": "Only POST requests are allowed."})


def Register_view(request):
    Reg_password = request.POST.get('password', '')
    Reg_confirm_password = request.POST.get('confirm_password', '')
    Reg_code = request.POST.get('phone_code', '')
    Reg_phone = request.POST.get('phone', '')
    Reg_username = request.POST.get('username', '')
    Reg_name = request.POST.get('name', '')
    Reg_id_number = request.POST.get('id_number', '')
    global Code

    print(Reg_password, Reg_confirm_password, Reg_code, Reg_phone, Reg_username, Reg_name, Reg_id_number)
    if Reg_password != Reg_confirm_password:
        context = {'reg_msg': '前后密码不一致'}
        return render(request, 'register.html', context)

    cursor = connection.cursor()
    cursor.execute("select id_number from user where id_number ='{}';".format(Reg_id_number))
    j_id_number = cursor.fetchone()
    print(j_id_number is not None, "hahaha")

    if j_id_number is not None:
        context = {'reg_msg': '此人已经注册'}
        return render(request, 'register.html', context)

    cursor.execute("select telephone from user where telephone ='{}';".format(Reg_phone))
    j_phone = cursor.fetchone()
    if j_phone is not None:
        context = {'reg_msg': '此电话号已经注册'}
        return render(request, 'register.html', context)

    cursor.execute("select user_account from user where user_account ='{}';".format(Reg_username))
    j_username = cursor.fetchone()
    if j_username is not None:
        context = {'reg_msg': '此账号已经注册'}
        return render(request, 'register.html', context)

    cursor.execute("select COUNT(*) from user;")
    user_cnt = cursor.fetchone()
    cursor.execute("insert into user values('{}', '{}', '{}', '{}', '{}', '{}');".format(int(user_cnt[0]) + 1, Reg_username, hashlib.sha256(Reg_password.encode()).hexdigest(), Reg_phone, Reg_name, Reg_id_number))
    return render(request, 'register.html')


def Forget_view(request):
    return render(request, 'forgot.html')


def Login_view(request):
    u = request.POST.get('username', '')
    p = request.POST.get('password', '')

    hash_p = hashlib.sha256(p.encode()).hexdigest()

    cursor = connection.cursor()
    cursor.execute("select user_password from user where user_account ='{}';".format(u))
    row = cursor.fetchone()
    if row is None:
        context = {'msg': '该用户不存在'}
        return render(request, 'login.html', context)
    else:
        db_password = row[0]
        if db_password == hash_p:
            return redirect(reverse('index'))
        else:
            context = {'msg': '用户名或密码错误'}
            return render(request, 'login.html', context)
