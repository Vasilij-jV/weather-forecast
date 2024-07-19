from django.shortcuts import render
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from geopy.geocoders import Nominatim
from django.shortcuts import render, get_object_or_404
from .forms import WeatherForecastForm


def calculation_forecast(request):
    # request_for_city_name = get_object_or_404(request)
    daily_dict = None
    if request.method == 'POST':
        form = WeatherForecastForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city_name']
            geolocator = Nominatim(user_agent="requestmeteo")

            # Название города, координаты которого мы хотим найти
            city = city_name

            # Поиск координат города
            location = geolocator.geocode(city)

            if location:
                print(f"Координаты {city}:")
                print(f"Широта: {location.latitude}, Долгота: {location.longitude}")
            else:
                print(f"Координаты для {city} не найдены")

            # Setup the Open-Meteo API client with cache and retry on error
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            openmeteo = openmeteo_requests.Client(session=retry_session)

            # Make sure all required weather variables are listed here
            # The order of variables in hourly or daily is important to assign them correctly below
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "hourly": "temperature_2m",
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_hours",
                          "precipitation_probability_max",
                          "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
                "timezone": "auto",
                "forecast_days": 1
            }
            responses = openmeteo.weather_api(url, params=params)

            # Process first location. Add a for-loop for multiple locations or weather models
            response = responses[0]
            print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
            print(f"Elevation {response.Elevation()} m asl")
            print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
            print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

            # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

            hourly_data = {"date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )}
            hourly_data["temperature_2m"] = hourly_temperature_2m

            hourly_dataframe = pd.DataFrame(data=hourly_data)
            print(hourly_dataframe)

            # Process daily data. The order of variables needs to be the same as requested.
            daily = response.Daily()
            daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
            daily_precipitation_hours = daily.Variables(2).ValuesAsNumpy()
            daily_precipitation_probability_max = daily.Variables(3).ValuesAsNumpy()
            daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
            daily_wind_gusts_10m_max = daily.Variables(5).ValuesAsNumpy()
            daily_wind_direction_10m_dominant = daily.Variables(6).ValuesAsNumpy()

            daily_data = {"date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )}
            daily_data["temperature_2m_max"] = int(daily_temperature_2m_max)
            daily_data["temperature_2m_min"] = int(daily_temperature_2m_min)
            daily_data["precipitation_hours"] = int(daily_precipitation_hours)
            daily_data["precipitation_probability_max"] = int(daily_precipitation_probability_max)
            daily_data["wind_speed_10m_max"] = int(daily_wind_speed_10m_max)
            daily_data["wind_gusts_10m_max"] = int(daily_wind_gusts_10m_max)
            daily_data["wind_direction_10m_dominant"] = int(daily_wind_direction_10m_dominant)

            daily_dataframe = pd.DataFrame(data=daily_data)
            daily_dict = daily_dataframe.to_dict(orient='records')
            print(daily_dict)
            return render(request, 'weatherforecastapp/city_name.html', {'daily_dict': daily_dict,
                                                                         'form': form})
    else:
        form = WeatherForecastForm()
    return render(request, 'weatherforecastapp/city_name.html', {'daily_dict': daily_dict,
                                                                 'form': form})


