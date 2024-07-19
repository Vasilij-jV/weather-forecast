from django.db import models
from django.conf import settings


class WeatherForecastModel(models.Model):
    city_name = models.CharField(max_length=30)
    temperature_2m_max = models.FloatField()
    temperature_2m_min = models.FloatField()
    precipitation_hours = models.FloatField()
    precipitation_probability_max = models.FloatField()
    wind_speed_10m_max = models.FloatField()
    wind_gusts_10m_max = models.FloatField()
    wind_direction_10m_dominant = models.FloatField()



