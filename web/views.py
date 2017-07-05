# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse
from json import JSONEncoder
from web.models import Expense, Income, User, Token
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render

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
