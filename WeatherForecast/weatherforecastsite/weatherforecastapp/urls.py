from django.urls import path
from .views import calculation_forecast

app_name = 'weatherforecastapp'

urlpatterns = [
    path('', calculation_forecast, name='calculation_forecast')
]
