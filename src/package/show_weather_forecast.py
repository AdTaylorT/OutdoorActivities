
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

from models.minutely_15_data import MinutelyData as m15
from models.minutely_15_data import Constants as cts
from errors.not_found_error import NotFoundError
from ext_service import weather_forecast as gwf
from ext_service import geo_coding as gc

def on_closing():
    plt.close('all')  # Close all matplotlib figures
    root.destroy()    # Destroy the tkinter window
    root.quit()       # Stop the mainloop

def focus_next_widget(event):
    event.widget.tk_focusNext().focus()
    return "break" # Prevents default tab behavior

def plot_forecast(minutely_15_dataframe):
    fig, ax = plt.subplots(figsize=(8, 4))
    # fmt = '[marker][line][color]'
    datestr = minutely_15_dataframe[cts.DATE.value]
    ax.plot(datestr, minutely_15_dataframe[m15.TEMP.api_name], '1:r', label = "Temperature (°F)")
    ax.plot(datestr, minutely_15_dataframe[m15.HUMIDITY.api_name], '2-.g', label = "Relative Humidity (%)")
    ax.plot(datestr, minutely_15_dataframe[m15.RAIN.api_name], '.--b', label = "Rain (in)")
    ax.plot(datestr, minutely_15_dataframe[m15.WIND_SPEED.api_name], '4--c', label = "Wind Speed (mph)")
    ax.plot(datestr, minutely_15_dataframe[m15.DIRECT_RADIATION.api_name], '*--y', label = "Direct Radiation (scaled to %)")

    ax.set_xlabel(cts.DATE.value.capitalize())
    ax.set_ylabel("Variable")
    ax.set_ylim(0, max(100, minutely_15_dataframe[m15.TEMP.api_name].max()))  # Set y-axis limits to 0-100%
    ax.set_title("Hourly Weather Forecast")
    ax.legend()
    ax.grid(True)
    ax.set_mouseover(True)  # Enable mouseover for better interactivity

    return fig

def get_dataframe(city_var_n, state_var_n, zipcode_var_n):
    city = city_var_n.get()
    state = state_var_n.get()
    zipcode = zipcode_var_n.get()
    try:
        gcode = gc.GeoCode()
        if city and state:
            location = gcode.fuzzy_name_lookup(city, state)
        elif zipcode:
            location = gcode.zipcode_lookup(zipcode)
        else:
            messagebox.showerror("Input Error", "Please enter a city and state or a zipcode.")
            return None
        # Extract lat/lon from DataFrame
        latlong = (location['lat'], location['lon'])
        forecast = gwf.WeatherForecast()
        df_15m = forecast.get_forecast(latlong)

        return pd.DataFrame(data = forecast.process_data(df_15m))
    except NotFoundError as nfe:
        messagebox.showerror("Location Not Found", str(nfe))
        print(f"Error: {nfe}")
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
        print(f"Error: {ve}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"Error: {e}")

    return None

def plot_dataframe(plot_frame_n, minutely_15_dataframe):
    fig = plot_forecast(minutely_15_dataframe)
    # Clear previous plot
    for widget in plot_frame_n.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=plot_frame_n)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Update window size to fit the new content
    root.update_idletasks()  # Make sure all widgets are updated
    root.geometry("")  # Reset geometry to let window resize to fit content

root = tk.Tk()
root.title("Weather Forecast Viewer")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Let the window size itself based on content
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set minimum window size to ensure controls are visible
root.minsize(600, 100)

# Center the window on the screen
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
x_position = (screen_width - (2*window_width)) // 2
y_position = (screen_height - window_height) // 4
root.geometry(f"+{x_position}+{y_position}")

root.lift()

mainframe = ttk.Frame(root, padding="10")
mainframe.pack(fill=tk.BOTH, expand=True)

input_frame = ttk.Frame(mainframe)
input_frame.pack(fill=tk.X, pady=5)

### Starting Location
ttk.Label(input_frame, text="Starting Location:\t").pack(side=tk.LEFT, padx=5)
tk.Event()
ttk.Label(input_frame, text="City:").pack(side=tk.LEFT)
city_var = tk.StringVar()
city_entry = ttk.Entry(input_frame, textvariable=city_var, width=15)
city_entry.pack(side=tk.LEFT, padx=2)
city_entry.bind('<Tab>', focus_next_widget)

ttk.Label(input_frame, text="State:").pack(side=tk.LEFT)
state_var = tk.StringVar()
state_entry = ttk.Entry(input_frame, textvariable=state_var, width=10)
state_entry.pack(side=tk.LEFT, padx=2)
state_entry.bind('<Tab>', focus_next_widget)

ttk.Label(input_frame, text="or Zipcode:").pack(side=tk.LEFT)
zipcode_var = tk.StringVar()
zipcode_entry = ttk.Entry(input_frame, textvariable=zipcode_var, width=10)
zipcode_entry.pack(side=tk.LEFT, padx=2)
zipcode_entry.bind('<Tab>', focus_next_widget)

plot_frame = ttk.Frame(mainframe)
plot_frame.pack(fill=tk.BOTH, expand=True)
# Bind Enter key to search for starting location
city_entry.bind('<Return>',
    lambda e: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))
state_entry.bind('<Return>',
    lambda e: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))
zipcode_entry.bind('<Return>',
    lambda e: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))

search_btn = ttk.Button(
    input_frame,
    text="Show Forecast",
    command=lambda: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))
search_btn.pack(fill=tk.X, side=tk.LEFT, padx=40)
search_btn.bind('<Tab>', focus_next_widget)
search_btn.bind('<Return>', lambda e: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))

# Add a separator between starting and ending locations
separator = ttk.Separator(mainframe, orient='horizontal')
separator.pack(fill=tk.X, pady=10, padx=5)

### Ending Location
input_frame2 = ttk.Frame(mainframe)
input_frame2.pack(fill=tk.X, pady=5)
ttk.Label(input_frame2, text="Ending Location:\t").pack(side=tk.LEFT, padx=5)

ttk.Label(input_frame2, text="City:").pack(side=tk.LEFT)
city_var2 = tk.StringVar()
city_entry2 = ttk.Entry(input_frame2, textvariable=city_var2, width=15)
city_entry2.pack(side=tk.LEFT, padx=2)
city_entry2.bind('<Tab>', focus_next_widget)

ttk.Label(input_frame2, text="State:").pack(side=tk.LEFT)
state_var2 = tk.StringVar()
state_entry2 = ttk.Entry(input_frame2, textvariable=state_var2, width=10)
state_entry2.pack(side=tk.LEFT, padx=2)
state_entry2.bind('<Tab>', focus_next_widget)

ttk.Label(input_frame2, text="or Zipcode:").pack(side=tk.LEFT)
zipcode_var2 = tk.StringVar()
zipcode_entry2 = ttk.Entry(input_frame2, textvariable=zipcode_var2, width=10)
zipcode_entry2.pack(side=tk.LEFT, padx=2)
zipcode_entry2.bind('<Tab>', focus_next_widget)

plot_frame2 = ttk.Frame(mainframe)
plot_frame2.pack(fill=tk.BOTH, expand=True)

# Bind Enter key to search for ending location
city_entry2.bind('<Return>',
    lambda e: plot_dataframe(plot_frame2, get_dataframe(city_var2, state_var2, zipcode_var2)))
state_entry2.bind('<Return>',
    lambda e: plot_dataframe(plot_frame2, get_dataframe(city_var2, state_var2, zipcode_var2)))
zipcode_entry2.bind('<Return>',
    lambda e: plot_dataframe(plot_frame2, get_dataframe(city_var2, state_var2, zipcode_var2)))

search_btn2 = ttk.Button(input_frame2,
                         text="Show Forecast",
                         command=lambda: plot_dataframe(plot_frame2, get_dataframe(city_var2, state_var2, zipcode_var2)))
search_btn2.pack(fill=tk.X, side=tk.LEFT, padx=40)
search_btn2.bind('<Tab>', focus_next_widget)
search_btn2.bind('<Return>', lambda e: plot_dataframe(plot_frame2, get_dataframe(city_var2, state_var2, zipcode_var2)))

root.mainloop()
