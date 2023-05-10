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
    global Code
    print(Code)
    if Reg_password != Reg_confirm_password:
        context = {'reg_msg': '前后密码不一致'}
        return render(request, 'register.html', context)


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
