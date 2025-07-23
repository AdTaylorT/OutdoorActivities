import openmeteo_requests

import requests_cache
import pandas as pd

from retry_requests import retry

class WeatherForecast():
    client = None

    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.client = openmeteo_requests.Client()

    def get_forecast(self, latlong):
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latlong[0],
            "longitude": latlong[1],
            "models": "gfs_seamless",
            "minutely_15": ["temperature_2m", "relative_humidity_2m", "rain", "wind_speed_10m"],
            "timezone": "America/New_York",
            "forecast_days": 1,
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "temperature_unit": "fahrenheit",
            "forecast_minutely_15": 48,
	        "past_minutely_15": 4
        }
        responses = self.client.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        #print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        #print(f"Elevation {response.Elevation()} m asl")
        #print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
        #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        return response

    def process_data(self, response):
        # Process minutely_15 data. The order of variables needs to be the same as requested.
        minutely_15 = response.Minutely15()
        if minutely_15:
            for x in range(0, 4):
                if not minutely_15.Variables(x):
                    print("error, no variables")
                    exit(1)
            minutely_15_temperature_2m = minutely_15.Variables(0).ValuesAsNumpy() # type: ignore
            minutely_15_relative_humidity_2m = minutely_15.Variables(1).ValuesAsNumpy() # type: ignore
            minutely_15_rain = minutely_15.Variables(2).ValuesAsNumpy() # type: ignore
            minutely_15_wind_speed_10m = minutely_15.Variables(3).ValuesAsNumpy() # type: ignore

            # Create a DataFrame with the processed data
            minutely_15_data = {"date": pd.date_range(
                start = pd.to_datetime(minutely_15.Time()+response.UtcOffsetSeconds(), unit = "s", utc = True),# type: ignore
                end = pd.to_datetime(minutely_15.TimeEnd()+response.UtcOffsetSeconds(), unit = "s", utc = True),# type: ignore
                freq = pd.Timedelta(seconds = minutely_15.Interval()),# type: ignore
                inclusive = "left"
            )}

            minutely_15_data["temperature_2m"] = minutely_15_temperature_2m # type: ignore
            minutely_15_data["relative_humidity_2m"] = minutely_15_relative_humidity_2m # type: ignore
            minutely_15_data["rain"] = minutely_15_rain # type: ignore
            minutely_15_data["wind_speed_10m"] = minutely_15_wind_speed_10m # type: ignore
            print(minutely_15_data)

            return minutely_15_data
