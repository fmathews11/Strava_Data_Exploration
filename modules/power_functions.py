from typing import Iterable
import numpy as np
from global_variables import CURRENT_LACTATE_THRESHOLD
from modules.objects.RideHub import RideHub
from modules.universal_functions import create_moving_average_array


def _convert_power_array_to_normalized_power_value(input_array: Iterable,
                                                   window_size: int = 30) -> int:
    """
    Returns a normalized power value from an array of data from a power meter.
    The default value for window size is 30, which is the widely accepted value
    """
    power_averages = create_moving_average_array(input_array=input_array, window_size=window_size)
    return round(np.mean(power_averages ** 4) ** 0.25)


def calculate_normalized_power_from_metrics_dict(input_dict: dict) -> int:
    """
    Returns an integer representing the normalized power from a StravaRide.metrics_dict dictionary.
    This function filters the data in such a way that the metrics_dict['moving'] array == True, so non-moving
    power measurements are ignored.

    Params:
    -------
    input_dict: dict - A dictionary from a StravaRide.metrics_dict

    Returns:
    --------
    An integer representing the normalized power for the ride associated with the user-provided metrics dictionary
    """
    # Guard clause (fail fast)
    if not isinstance(input_dict, dict):
        raise TypeError(f"Argument provided for the input_dict parameter must be a dictionary. {type(input_dict)}"
                        f"was passed")

    # Grab the boolean array - [False, True,True..etc]
    boolean_array = np.array(input_dict.get('moving'))
    # Return the subset array
    return _convert_power_array_to_normalized_power_value(np.array(input_dict.get('watts'))[boolean_array])


def identify_heart_rate_zone(heart_rate_value: int) -> int:
    """Identifies heart rate zones based on the lactate threshold in the global variables file.
    This method was researched and proposed by Andrew Coggan"""
    if heart_rate_value > CURRENT_LACTATE_THRESHOLD:
        return 5
    if heart_rate_value >= round(CURRENT_LACTATE_THRESHOLD * 0.95, 0):
        return 4
    if heart_rate_value >= round(CURRENT_LACTATE_THRESHOLD * 0.89, 0):
        return 3
    if heart_rate_value >= round(CURRENT_LACTATE_THRESHOLD * 0.8, 0):
        return 2
    return 1


def calculate_training_stress_score(total_seconds: int,
                                    normalized_power: float,
                                    intensity_factor: float,
                                    ftp: int) -> float:

    """Uses TrainerRoad's method to determine training stress score"""
    return 100*((total_seconds * normalized_power * intensity_factor) / (ftp * 3600))


def create_individual_ride_power_curve(ride_hub: RideHub,
                                       ride_id: int) -> np.ndarray:
    """Returns an array representing an individual ride curve.
    The array is returned in such a way where the index value represents the number of seconds,
    and the value represents the maximum average power observed over that time window.

    For example, a value of 450 at index position 10 means that 450 watts was the maximum average power over a 10-second
    window throughout the ride.

    These are calculated via sliding window algorithm
    """

    watts_array = ride_hub[ride_id].metrics_dict['watts']
    return np.array([np.max(create_moving_average_array(watts_array, i)) for i in range(1, len(watts_array) + 1)])