from django.contrib.auth import authenticate, login
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


def toForget_view(request):
    return render(request, 'forgot.html')


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
    Reg_confirm_password = request.POST.get('confirm-password', '')
    Reg_code = request.POST.get('phone-code', '')
    Reg_phone = request.POST.get('phone', '')
    Reg_username = request.POST.get('username', '')
    Reg_name = request.POST.get('name', '')
    Reg_id_number = request.POST.get('id-number', '')

    if Code != Reg_code:
        context = {'reg_msg': '验证码错误'}
        return render(request, 'register.html', context)

    if Reg_password != Reg_confirm_password:
        context = {'reg_msg': '前后密码不一致'}
        return render(request, 'register.html', context)

    cursor = connection.cursor()
    cursor.execute("select id_number from user where id_number ='{}';".format(Reg_id_number))
    j_id_number = cursor.fetchone()

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

    cursor.execute("call new_user(%s, %s, %s, %s, %s)", (Reg_username, hashlib.sha256(Reg_password.encode()).hexdigest(), Reg_phone, Reg_name, Reg_id_number))
    # cursor.execute("insert into user values('{}', '{}', '{}', '{}', '{}', '{}');".format(int(user_cnt[0]) + 1, Reg_username, hashlib.sha256(Reg_password.encode()).hexdigest(), Reg_phone, Reg_name, Reg_id_number))
    context = {'reg_msg_suss': '注册成功'}
    return render(request, 'register.html', context)


def Forget_view(request):
    Fog_phone = request.POST.get('phone', '')
    Fog_code = request.POST.get('phone-code', '')
    Fog_password = request.POST.get('password', '')
    Fog_confirm_password = request.POST.get('confirm-password', '')

    if Code != Fog_code:
        context = {'fog_msg': '验证码错误'}
        return render(request, 'forgot.html', context)

    if Fog_password != Fog_confirm_password:
        context = {'fog_msg': '前后密码不一致'}
        return render(request, 'forgot.html', context)

    cursor = connection.cursor()
    cursor.execute("select telephone from user where telephone ='{}';".format(Fog_phone))
    j_phone = cursor.fetchone()
    if j_phone is not None:
        context = {'fog_msg_suss': '修改密码成功'}
        cursor.execute("call update_passwd(%s, %s)", (hashlib.sha256(Fog_password.encode()).hexdigest(), Fog_phone))
        # cursor.execute("update user set user_password = '{}' where telephone = '{}';".format(hashlib.sha256(Fog_password.encode()).hexdigest(), Fog_phone))
        return render(request, 'forgot.html', context)
    else:
        context = {'fog_msg': '此手机号不存在'}
        return render(request, 'forgot.html', context)


def toLogout_view(request):
    return render(request, 'logout.html')


def Logout_view(request):
    Log_phone = request.POST.get('phone')
    Log_code = request.POST.get('phone-code')

    if Code != Log_code:
        context = {'msg': '验证码错误'}
        return render(request, 'logout.html', context)

    cursor = connection.cursor()
    cursor.execute("select telephone from user where telephone ='{}';".format(Log_phone))
    j_phone = cursor.fetchone()
    if j_phone is not None:
        cursor.execute("call delete_user_from_telephone(%s)", Log_phone)
        # cursor.execute("delete from user where telephone = '{}';".format(Log_phone))
        context = {'msg_suss': '注销账户成功'}
        return render(request, 'logout.html', context)
    else:
        context = {'msg': '此手机号不存在'}
        return render(request, 'logout.html', context)


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
            request.session['username'] = u
            return redirect(reverse('index'))
        else:
            context = {'msg': '用户名或密码错误'}
            return render(request, 'login.html', context)


def exit_view(request):
    request.session.delete(request.session.session_key)
    return redirect('/')
