from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.db import connection
import hashlib


# Create your views here.
def toLogin_view(request):
    return render(request, 'login.html')


def Register_view(request):
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
