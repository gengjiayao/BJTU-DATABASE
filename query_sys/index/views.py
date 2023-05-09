from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import hashlib


# Create your views here.
def Index_view(request):
    return render(request, 'index.html')
