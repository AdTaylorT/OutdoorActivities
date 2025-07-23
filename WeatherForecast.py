import openmeteo_requests

import requests_cache
import pandas as pd
import numpy as np

from retry_requests import retry

from minutely_15_data import minutely_15_data as m15

class WeatherForecast():
    client: openmeteo_requests.Client | None = None

    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        import os
        import tempfile
        
        # Create cache directory in user's temp directory
        cache_dir = os.path.join(tempfile.gettempdir(), 'weatherbike')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, 'weather_cache.sqlite')
        
        # Initialize cache with 30 minute expiration
        cache_session = requests_cache.CachedSession(
            cache_file,
            expire_after=1800,
            backend='sqlite'
        )
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.client = openmeteo_requests.Client(session=retry_session) # type: ignore
        
    def get_forecast(self, latlong):
        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        min_15_param =["temperature_2m", "relative_humidity_2m", "rain", "wind_speed_10m", "direct_radiation"]
        params = {
            "latitude": latlong[0],
            "longitude": latlong[1],
            "models": "gfs_seamless",
            "minutely_15": min_15_param,
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
        minutely_15_data = {}
        if minutely_15:
            for x in m15:
                if not minutely_15.Variables(x.index):
                    print("error, no variables")
                    exit(1)
                else:
                    minutely_15_data[x.api_name] = minutely_15.Variables(x.index).ValuesAsNumpy()

            # Do some shenanigans with direct radiation
            # to ensure values are scaled down to a "100"
            # TODO probably track this in another field, so we can show the scale on the plot
            minutely_15_direct_radiation = minutely_15_data[m15.DIRECT_RADIATION.api_name]
            while max(minutely_15_direct_radiation) > 100: # Ensure values are scaled down to a percentage
                minutely_15_direct_radiation = minutely_15_direct_radiation / 10
            minutely_15_data[m15.DIRECT_RADIATION.api_name] = minutely_15_direct_radiation

            # Create a DataFrame with the processed data
            minutely_15_data["date"] = pd.date_range(
                start = pd.to_datetime(minutely_15.Time()+response.UtcOffsetSeconds(), unit = "s", utc = True),
                end = pd.to_datetime(minutely_15.TimeEnd()+response.UtcOffsetSeconds(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = minutely_15.Interval()),
                inclusive = "left"
            )

            minutely_15_data[m15.DIRECT_RADIATION.api_name] = minutely_15_direct_radiation

            print(minutely_15_data)

            return minutely_15_data
