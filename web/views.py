# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from json import JSONEncoder
from web.models import Expense, Income, User, Token, Passwordresetcodes
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.db.models import Sum, Count
#import postmark.PMMail
#from postmark import PMMail
import requests
from postmark import *
import random, string, time
random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

@csrf_exempt
def generalstat(request):
    this_token  = request.POST['token']
    this_user = User.objects.filter(token__token =this_token).get()
    income = Income.objects.filter(user=this_user).aggregate(Count('amount'), Sum('amount'))
    expense = Expense.objects.filter(user=this_user).aggregate(Count('amount'), Sum('amount'))
    context = {}
    context['income'] = income
    context['expense'] = expense
    return JsonResponse(context, encoder=JSONEncoder)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
def index(request):
    context = {}
    return render(request, 'index.html', context)

def grecaptcha_verify(request):
    data = request.POST
    captcha_rs = data.get('g-recaptcha-response')
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': captcha_rs,
        'remoteip': get_client_ip(request)
    }
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    return verify_rs.get("success", False)



def register(request):
    if request.POST.has_key('requestcode'): #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        #is this spam? check reCaptcha
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'} #TODO: forgot password
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists(): # duplicate email
            context = {'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)

        if not User.objects.filter(username = request.POST['username']).exists(): #if user does not exists
                code = random_str(28)
                now = datetime.now()
                email = request.POST['email']
                password = make_password(request.POST['password'])
                username = request.POST['username']
                temporarycode = Passwordresetcodes (email = email, time = now, code = code, username=username, password=password)
                temporarycode.save()
                message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
                                 subject ="فعال سازی اکانب بستون",
                                 sender = "r.ahmadi1983@reshadahmadi.info",
                                 #to = email,
                                 to = "reah@hms.se",
                                 text_body = " برای فعال کردن اکانت بستون خود روی لینک روبرو کلیک کنید: 7{}?email={}&code={}".format(request.build_absolute_uri('accounts/register'),email, code),
                                 tag = "account request")
                message.send()
                context = {'message': 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)
    elif request.GET.has_key('code'): # user clicked on code
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists(): #if code is in tempor ary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password, email=email)
            this_token = random_str(48)
            token = Token.objects.create(user=newuser, token=this_token)
            Passwordresetcodes.objects.filter(code=code).delete() #delete the temporary activation code from db
            context = {'message': 'اکانت شما ساخته شد. توکن شما {} است. آن را ذخیره کنید چون دیگر نمایش داده نخواهد شد! جدی!'.format(this_token)}
            return render(request, 'login.html', context)
        else:
            context = {'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)
@csrf_exempt
# Create your views here.
def submit_income(request):
    """user submit an income"""
    #TODO;
    print request.POST
    this_token  = request.POST['token']
    this_user = User.objects.filter(token__token =this_token).get()
    if 'date' not in request.POST:
        now = datetime.now()

    amount = request.POST['amount']
    Income.objects.create(user = this_user, text = request.POST['text'],
    amount = request.POST['amount'], date = now)
    return JsonResponse(
    {
        'status':'ok',
    },encoder = JSONEncoder)


@csrf_exempt
# Create your views here.
def submit_expense(request):
    """user submit an expense"""
    #TODO;
    print request.POST
    this_token  = request.POST['token']
    this_user = User.objects.filter(token__token =this_token).get()
    if 'date' not in request.POST:
        now = datetime.now()

    amount = request.POST['amount']
    Expense.objects.create(user = this_user, text = request.POST['text'],
    amount = request.POST['amount'], date = now)
    return JsonResponse(
    {
        'status':'ok',
    },encoder = JSONEncoder)
