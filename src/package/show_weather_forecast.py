import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure as mpl_figure
import matplotlib.pyplot as plt
import pandas as pd

from models.minutely_15_data import MinutelyData as m15
from models.minutely_15_data import Constants as cts
from errors.not_found_error import NotFoundError
from ext_service import weather_forecast as gwf
from ext_service import geo_coding as gc

def on_closing() -> None:
    """
    Handle hitting the applications "X" button and closing out the application,
    intercept and make sure we destroy TK objects and the plot objects
    """
    plt.close('all')  # Close all matplotlib figures
    root.destroy()    # Destroy the tkinter window
    root.quit()       # Stop the mainloop

def focus_next_widget(event) -> str:
    """
    handle tab focus action
    """
    event.widget.tk_focusNext().focus()
    return "break" # Prevents default tab behavior

def destroy_last_stop() -> None:
    """
    remove the content (3 elements) from adding in multiple stops
    """
    children = mainframe.winfo_children()
    count_children = len(children)
    if ttk.Separator in [type(c) for c in children]:
        for c in reversed(children):
            if count_children <= root_frame_count:
                # safe guard removing too many children
                # shouldn't happen anyway, but ... rather safe than sorry
                return
            if type(c) == ttk.Separator:
                c.destroy()
                return
            c.destroy()
            count_children -= 1

def add_location_form() -> None:
    """
    for each location the user adds by clicking the 'add location' button
    each location has a city, state, combo, or a zipcode

    setup the button, tab, and and return lambda binds.
    """
    # are we at the "minimum" number of manditory children?
    if len(mainframe.winfo_children()) >= root_frame_count:
        # Add a separator between starting and any other location
        separator = ttk.Separator(mainframe, orient='horizontal')
        separator.pack(fill=tk.X, pady=10, padx=5)

    def create_var(input_frame: ttk.Frame, width=15) -> tk.StringVar:
        """ nested helper to add in a dynamic variable box """
        var = tk.StringVar()
        entry = ttk.Entry(input_frame, textvariable=var, width=width)
        entry.pack(side=tk.LEFT, padx=2)

        return var

    input_frame = ttk.Frame(mainframe)
    input_frame.pack(fill=tk.X, pady=5)
    ### Starting Location
    ttk.Label(input_frame, text="Location:\t").pack(side=tk.LEFT, padx=5)

    ttk.Label(input_frame, text="City:").pack(side=tk.LEFT)
    city_var = create_var(input_frame)

    ttk.Label(input_frame, text="State:").pack(side=tk.LEFT)
    state_var = create_var(input_frame)

    ttk.Label(input_frame, text="or Zipcode:").pack(side=tk.LEFT)
    zipcode_var = create_var(input_frame, 7)

    plot_frame = ttk.Frame(mainframe)
    plot_frame.pack(fill=tk.BOTH, expand=True)

    search_btn = ttk.Button(
        input_frame,
        text="Show Forecast",
        command=lambda: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))
    search_btn.pack(fill=tk.X, side=tk.LEFT, padx=40)

    # bind tab, and return functionality for all button and text_fields (Entry)
    for c in input_frame.winfo_children():
        if type(c) in [ttk.Button, ttk.Entry]:
            c.bind('<Tab>', focus_next_widget)
            c.bind('<Return>', lambda e: plot_dataframe(plot_frame, get_dataframe(city_var, state_var, zipcode_var)))

def plot_forecast(minutely_15_dataframe: pd.DataFrame) -> mpl_figure:
    """
    create a plot and render it in tkinter for the data returned to us from the meteo weather API
    params:
        minutely_15_dataframe:
        data frame with the 15 minute interval data
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    # fmt = '[marker][line][color]'
    # fmt is the 3rd parameter, and kinda sucks.

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
    # Enable mouseover for better interactivity
    # allegedly, doesn't really do anything...
    # is that because somethings wonky about how it's embedded?
    ax.set_mouseover(True)

    return fig

def get_dataframe(city_var_n, state_var_n, zipcode_var_n):
    """
    get the latitude and longitude from the GeoCode library,
    pass that information into the open Meteo API via our wrapper,

    """
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

        if location is None:
            messagebox.showerror("Input Error", "Could not find: city and state or a zipcode.")
            return None

        # Extract lat/lon from DataFrame
        latlong = (location['lat'], location['lon'])
        forecast = gwf.WeatherForecast()
        df_15m = forecast.get_forecast(latlong)

        return pd.DataFrame(data = forecast.process_data(df_15m))
    except NotFoundError as nfe:
        messagebox.showerror("Location Not Found", str(nfe))
        print(f"Error: {nfe.with_traceback}")
    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
        print(f"Error: {ve.with_traceback}")

    return None

def plot_dataframe(plot_frame_n: ttk.Frame, minutely_15_dataframe: pd.DataFrame):
    # shortcut if we don't get data, because we chain methods in the lambda
    # probably a cleaner way to do it, but it's UI stuff so what do i know
    if minutely_15_dataframe is None or minutely_15_dataframe.empty:
        return None
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
root.minsize(661, 100)

# Center the window on the screen
window_width = root.winfo_reqwidth()
window_height = root.winfo_reqheight()
x_position = (screen_width - (4 * window_width)) // 2
y_position = (screen_height - window_height) // 4
root.geometry(f"+{x_position}+{y_position}")
root.lift()
root.grab_release()

mainframe = ttk.Frame(root, padding="10")
mainframe.pack(fill=tk.BOTH, expand=True)

input_frame = ttk.Frame(mainframe)
input_frame.pack(fill=tk.X, pady=5)
add_location_btn = ttk.Button(input_frame,
                         text="Add Stop",
                         command=lambda: add_location_form())
add_location_btn.pack(fill=tk.X, side=tk.LEFT, padx=10)
add_location_btn.bind('<Tab>', focus_next_widget)
add_location_btn.bind('<Return>', lambda e: add_location_form())

root_frame_count = len(mainframe.winfo_children())+1
add_location_form()
remove_loc_btn = ttk.Button(input_frame,
                         text="Remove Last",
                         command=lambda: destroy_last_stop())
remove_loc_btn.pack(fill=tk.X, side=tk.LEFT, padx=10)

root.mainloop()
