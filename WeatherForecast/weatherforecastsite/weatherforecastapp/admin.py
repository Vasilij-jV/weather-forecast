from django.contrib import admin
from .models import WeatherForecastModel


@admin.register(WeatherForecastModel)
class WeatherForecastModelAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'temperature_2m_max', 'temperature_2m_min', 'precipitation_hours',
                    'precipitation_probability_max', 'wind_speed_10m_max', 'wind_gusts_10m_max',
                    'wind_direction_10m_dominant')
    search_fields = ('city_name', 'temperature_2m_max', 'temperature_2m_min')
    list_filter = ('city_name', 'temperature_2m_max', 'temperature_2m_min')
