from django import forms
from .models import WeatherForecastModel


class WeatherForecastForm(forms.ModelForm):
    city_name = forms.CharField(label='Enter a city name')

    class Meta:
        model = WeatherForecastModel
        fields = ['city_name',]



