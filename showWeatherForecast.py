
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

import WeatherForecast as gwf
import geoCoding as gc

def on_closing():
    plt.close('all')  # Close all matplotlib figures
    root.destroy()    # Destroy the tkinter window
    root.quit()       # Stop the mainloop

def plot_forecast(minutely_15_dataframe):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(minutely_15_dataframe["date"], minutely_15_dataframe["temperature_2m"], label = "Temperature (°F)")
    ax.plot(minutely_15_dataframe["date"], minutely_15_dataframe["rain"], label = "Rain (in)", linestyle=':')
    ax.plot(minutely_15_dataframe["date"], minutely_15_dataframe["wind_speed_10m"], label = "Wind Speed (mph)", linestyle='--')
    ax.plot(minutely_15_dataframe["date"], minutely_15_dataframe["relative_humidity_2m"], label = "Relative Humidity (%)", linestyle='-.')
    ax.set_xlabel("Date")
    ax.set_ylabel("Variable")
    ax.set_title("Hourly Weather Forecast")
    ax.legend()
    return fig

def get_and_plot(city_varN, state_varN, zipcode_varN, plot_frameN):
    city = city_varN.get()
    state = state_varN.get()
    zipcode = zipcode_varN.get()
    try:
        gcode = gc.myGeoCode()
        if city and state:
            end_loc = gcode.fuzzy_name_lookup(city, state)
        elif zipcode:
            end_loc = gcode.zipcode_lookup(zipcode)
        else:
            messagebox.showerror("Input Error", "Please enter a city and state or a zipcode.")
            return
        # Extract lat/lon from DataFrame
        latlong = (end_loc['lat'], end_loc['lon'])
        forecast = gwf.WeatherForecast()
        df_15m = forecast.get_forecast(latlong)
        minutely_15_dataframe = pd.DataFrame(data = forecast.process_data(df_15m))
        fig = plot_forecast(minutely_15_dataframe)
        # Clear previous plot
        for widget in plot_frameN.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=plot_frameN)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"Error: {e}")

root = tk.Tk()
root.title("Weather Forecast Viewer")
root.protocol("WM_DELETE_WINDOW", on_closing)

mainframe = ttk.Frame(root, padding="10")
mainframe.pack(fill=tk.BOTH, expand=True)

input_frame = ttk.Frame(mainframe)
input_frame.pack(fill=tk.X, pady=5)

### Starting Location
ttk.Label(input_frame, text="Starting Locations:").pack(side=tk.LEFT, padx=5)

ttk.Label(input_frame, text="City:").pack(side=tk.LEFT)
city_var = tk.StringVar()
city_entry = ttk.Entry(input_frame, textvariable=city_var, width=15)
city_entry.pack(side=tk.LEFT, padx=2)

ttk.Label(input_frame, text="State:").pack(side=tk.LEFT)
state_var = tk.StringVar()
state_entry = ttk.Entry(input_frame, textvariable=state_var, width=10)
state_entry.pack(side=tk.LEFT, padx=2)

ttk.Label(input_frame, text="or Zipcode:").pack(side=tk.LEFT)
zipcode_var = tk.StringVar()
zipcode_entry = ttk.Entry(input_frame, textvariable=zipcode_var, width=10)
zipcode_entry.pack(side=tk.LEFT, padx=2)

plot_frame = ttk.Frame(mainframe)
plot_frame.pack(fill=tk.BOTH, expand=True)

search_btn = ttk.Button(input_frame, text="Show Forecast", command=lambda: get_and_plot(city_var, state_var, zipcode_var, plot_frame))
search_btn.pack(side=tk.LEFT, padx=5)

### Ending Location
input_frame2 = ttk.Frame(mainframe)
input_frame2.pack(fill=tk.X, pady=5)
ttk.Label(input_frame2, text="Ending Locations:").pack(side=tk.LEFT, padx=5)

ttk.Label(input_frame2, text="City:").pack(side=tk.LEFT)
city_var2 = tk.StringVar()
city_entry2 = ttk.Entry(input_frame2, textvariable=city_var2, width=15)
city_entry2.pack(side=tk.LEFT, padx=2)

ttk.Label(input_frame2, text="State:").pack(side=tk.LEFT)
state_var2 = tk.StringVar()
state_entry2 = ttk.Entry(input_frame2, textvariable=state_var2, width=10)
state_entry2.pack(side=tk.LEFT, padx=2)

ttk.Label(input_frame2, text="or Zipcode:").pack(side=tk.LEFT)
zipcode_var2 = tk.StringVar()
zipcode_entry2 = ttk.Entry(input_frame2, textvariable=zipcode_var2, width=10)
zipcode_entry2.pack(side=tk.LEFT, padx=2)

plot_frame2 = ttk.Frame(mainframe)
plot_frame2.pack(fill=tk.BOTH, expand=True)

search_btn2 = ttk.Button(input_frame2, text="Show Forecast", command=lambda: get_and_plot(city_var2, state_var2, zipcode_var2, plot_frame2))
search_btn2.pack(side=tk.LEFT, padx=5)

root.mainloop()