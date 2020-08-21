from bot.views import UpdateBot
from django.urls import path

urlpatterns = [
    path('telegram', UpdateBot.as_view(), name='update')
]
