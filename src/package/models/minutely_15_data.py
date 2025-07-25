from enum import Enum

class Constants(Enum):
    DATE = "date"

class MinutelyData(Enum):
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
    print(f"Enum member: {MinutelyData.TEMP}")
    print(f"Enum name: {MinutelyData.TEMP.name}")
    print(f"Full value (tuple): {MinutelyData.TEMP.value}")
    print(f"Index: {MinutelyData.TEMP.index}")
    print(f"API name: {MinutelyData.TEMP.api_name}")

    # Example of how to use the enum
    for weather_param in MinutelyData:
        print(f"{weather_param.name}: index={weather_param.index}, api_name={weather_param.api_name}")