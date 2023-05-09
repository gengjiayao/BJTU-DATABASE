from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.


def toLogin_view(request):
    return render(request, 'login.html')


def Login_view(request):
    u = request.POST.get('username', '')
    p = request.POST.get('password', '')

    if u == 'admin' and p == '123456':
        return HttpResponse("登陆成功")
    else:
        context = {'msg': '用户名或密码错误'}
        return render(request, 'login.html', context)
