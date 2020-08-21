from django.contrib import admin
from .models import User

# Register your models here.

admin.site.site_header = 'Crystal Cash Admin'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'today_cash', 'luck_point')
    list_filter = ('today_cash', 'luck_point')
    search_fields = ('name', 'today_cash')
