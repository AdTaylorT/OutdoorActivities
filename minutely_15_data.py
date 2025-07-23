from enum import Enum, auto

class minutely_15_data(Enum):
    TEMP = (0, "temperature_2m")
    HUMIDITY = (1, "relative_humidity_2m")
    RAIN = (2, "rain")
    WIND_SPEED = (3, "wind_speed_10m")
    DIRECT_RADIATION = (4, "direct_radiation")

    def __init__(self, index: int, name: str):
        self.index = index
        self.api_name = name

if __name__ == "__main__":
    # Print all available information for TEMP
    print(f"Enum member: {minutely_15_data.TEMP}")
    print(f"Enum name: {minutely_15_data.TEMP.name}")
    print(f"Full value (tuple): {minutely_15_data.TEMP.value}")
    print(f"Index: {minutely_15_data.TEMP.index}")
    print(f"API name: {minutely_15_data.TEMP.api_name}")
    
    # Example of how to use the enum
    for weather_param in minutely_15_data:
        print(f"{weather_param.name}: index={weather_param.index}, api_name={weather_param.api_name}")