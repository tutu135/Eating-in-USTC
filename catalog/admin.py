from django.contrib import admin
from .models import RESTAURANT, DISH, COMMENT, REPLY, DELETE_RESTA, MANAGER_REG

# Register your models here.
admin.site.register(RESTAURANT)
admin.site.register(DISH)
admin.site.register(COMMENT)
admin.site.register(REPLY)
admin.site.register(DELETE_RESTA)
admin.site.register(MANAGER_REG)
