# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Register your models here.
from django.contrib import admin
from .models import Expense
from .models import Income
from .models import Token

admin.site.register(Token)
admin.site.register(Expense)
admin.site.register(Income)
