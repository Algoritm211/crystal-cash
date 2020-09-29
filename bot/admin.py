from django.contrib import admin
from .models import User, Ticket

# Register your models here.

admin.site.site_header = 'Crystal Cash Admin'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'today_cash', 'minigame_counter_date')
    list_filter = ('today_cash',)
    search_fields = ('name', 'today_cash')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)

