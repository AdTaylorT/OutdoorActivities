
import matplotlib.pyplot as plt
import pandas as pd

import WeatherForecast as gwf
import geoCoding as gc

forecast = gwf.WeatherForecast()
latlong = (38.8048, -77.0469)  # Example coordinates
gcode = gc.myGeoCode()
end_loc = gcode.fuzzy_name_lookup('Vienna', 'Virginia')
start_loc = gcode.zipcode_lookup('22314')

df_15m = forecast.get_forecast((end_loc['lat'], end_loc['lon']))
minutely_15_dataframe = pd.DataFrame(data = forecast.process_data(df_15m))

# Plot the hourly temperature data
plt.plot(minutely_15_dataframe["date"], minutely_15_dataframe["temperature_2m"], label = "Temperature (°F)")
plt.plot(minutely_15_dataframe["date"], minutely_15_dataframe["rain"], label = "Rain (in)", linestyle=':')
plt.plot(minutely_15_dataframe["date"], minutely_15_dataframe["wind_speed_10m"], label = "Wind Speed (mph)", linestyle='--')
plt.plot(minutely_15_dataframe["date"], minutely_15_dataframe["relative_humidity_2m"], label = "Relative Humidity (%)", linestyle='-.')
plt.xlabel("Date")
plt.ylabel("Variable")
plt.title("Hourly Temperature Forecast")
plt.legend()
plt.show()