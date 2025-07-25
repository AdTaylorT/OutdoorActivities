from enum import Enum, auto

import numpy as np

class HeatDanger(Enum):
    NORMAL = auto()      # Below 80°F
    CAUTION = auto()     # 80-90°F
    EXTREME_CAUTION = auto()  # 90-103°F
    DANGER = auto()      # 103-124°F
    EXTREME_DANGER = auto()   # 125°F+


class HeatIndex:
    # Heat index danger thresholds (°F)
    HEAT_NORMAL = 80
    HEAT_CAUTION = 90
    HEAT_EXTREME_CAUTION = 103
    HEAT_DANGER = 125


class HeatIndexLookup:
    # Heat index lookup table
    # Rows: Relative Humidity (40% to 100% in 5% steps)
    # Columns: Temperature (80°F to 110°F in 2°F steps)
    _heat_index_table = np.array([
    [80, 81, 83, 85, 88, 91, 94, 97, 101, 105, 109, 114, 119, 124, 130, 136],  # 40%
    [80, 82, 84, 87, 89, 93, 96, 100, 104, 109, 114, 119, 124, 130, 137],      # 45%
    [81, 83, 85, 88, 91, 95, 99, 103, 108, 113, 118, 124, 131, 137],          # 50%
    [81, 84, 86, 89, 93, 97, 101, 106, 112, 117, 124, 130, 137],              # 55%
    [82, 84, 88, 91, 95, 100, 105, 110, 116, 123, 129, 137],                  # 60%
    [82, 85, 89, 93, 98, 103, 108, 114, 121, 128, 136],                       # 65%
    [83, 86, 90, 95, 100, 105, 112, 119, 126, 134],                           # 70%
    [84, 88, 92, 97, 103, 109, 116, 124, 132],                                # 75%
    [84, 89, 94, 100, 106, 113, 121, 129],                                    # 80%
    [85, 90, 96, 102, 110, 117, 126, 135],                                    # 85%
    [86, 91, 98, 105, 113, 122, 131],                                         # 90%
    [86, 93, 100, 108, 117, 127],                                             # 95%
    [87, 95, 103, 112, 121, 132]                                              # 100%
])

    @staticmethod
    def get_heat_index(temp_f, humidity):
        """
        Calculate heat index given temperature (°F) and relative humidity (%)
        Returns the heat index temperature in °F
        """
        if temp_f < 80 or humidity < 40:
            return temp_f  # Below table bounds, return actual temperature

        # Round inputs to nearest table values
        temp_idx = round((temp_f - 80) / 2)  # Temperature starts at 80°F with 2°F steps
        humidity_idx = round((humidity - 40) / 5)  # Humidity starts at 40% with 5% steps

        # Bounds checking
        if (temp_idx >= HeatIndexLookup._heat_index_table.shape[1]
            or humidity_idx >= HeatIndexLookup._heat_index_table.shape[0]):
            return 150  # Above table bounds, return dangerous high value

        return HeatIndexLookup._heat_index_table[humidity_idx, temp_idx]

    @staticmethod
    def get_danger_level(heat_index_temp):
        """
        Determine the danger level based on the heat index temperature
        Returns a HeatDanger enum value
        """
        if heat_index_temp < HeatIndex.HEAT_NORMAL:
            return HeatDanger.NORMAL
        if heat_index_temp < HeatIndex.HEAT_CAUTION:
            return HeatDanger.CAUTION
        if heat_index_temp < HeatIndex.HEAT_EXTREME_CAUTION:
            return HeatDanger.EXTREME_CAUTION
        if heat_index_temp < HeatIndex.HEAT_DANGER:
            return HeatDanger.DANGER

        return HeatDanger.EXTREME_DANGER
