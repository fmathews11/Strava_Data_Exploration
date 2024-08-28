import json
from typing import Any
import pandas as pd
from modules.objects.RideHub import RideHub
from modules.power_functions import calculate_normalized_power_from_metrics_dict, calculate_training_stress_score
from global_variables import CURRENT_FTP

master_column_list = ['resource_state',
                      'id',
                      'athlete_id',
                      'name',
                      'distance',
                      'moving_time',
                      'moving_time_seconds',
                      'elapsed_time',
                      'elapsed_time_seconds',
                      'total_elevation_gain',
                      'type',
                      'sport_type',
                      'workout_type',
                      'start_date',
                      'location_city',
                      'location_state',
                      'location_country',
                      'achievement_count',
                      'kudos_count',
                      'comment_count',
                      'athlete_count',
                      'photo_count',
                      'map_id',
                      'polyline',
                      'trainer',
                      'manual',
                      'private',
                      'visibility',
                      'flagged',
                      'gear_id',
                      'starting_latitude',
                      'starting_longitude',
                      'ending_latitude',
                      'ending_longitude',
                      'average_speed',
                      'max_speed',
                      'average_cadence',
                      'average_temp',
                      'average_watts',
                      'max_watts',
                      'weighted_average_watts',
                      'kilojoules',
                      'device_watts',
                      'has_heartrate',
                      'average_heartrate',
                      'max_heartrate',
                      'heartrate_opt_out',
                      'display_hide_heartrate_option',
                      'elev_high',
                      'elev_low',
                      'upload_id',
                      'upload_id_str',
                      'external_id',
                      'from_accepted_tag',
                      'pr_count',
                      'total_photo_count',
                      'has_kudoed',
                      'suffer_score',
                      'normalized_power',
                      'intensity_factor',
                      'tss']

with open('data/saved_strava_rides.json', 'r') as f:
    ride_hub = RideHub(*json.load(f))


# Internal
def _convert_mps_to_mph(value: float) -> float:
    """Converts meters per second to miles per hour"""
    return value * 2.23694


def _convert_meters_to_miles(value: float) -> float:
    """Converts meters to miles"""
    return value * 0.000621371


def _convert_meters_to_feet(value: float) -> float:
    """Converts meters to feet"""
    return value * 3.28084


def _grab_element_of_list_if_exists(input_list: list, element_number: int) -> Any:
    """Simple function to return a specific element of a list if it exists. Returns None otherwise"""
    return input_list[element_number] if input_list else None


def _convert_total_seconds_to_HMS_format(total_seconds: int) -> str:
    """
    Function converts an integer value representing total seconds elapsed into a string representing
    "Hours: minutes: seconds"
    """
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes}:{seconds}"


def _apply_training_stress_score(row):
    """
    Quick mapping function to apply the TSS calculation across several fields.
    Will be used in tandem with Pandas' `apply()` method.
    """
    return calculate_training_stress_score(row.moving_time_seconds,
                                           row.normalized_power,
                                           row.intensity_factor,
                                           CURRENT_FTP)


def create_normalized_power_dict() -> dict:
    """
    Returns a dictionary for format {ride_id:normalized power value}.
    This is primarily used as a mapping for the summary dataframe
    """
    return {ride.id: calculate_normalized_power_from_metrics_dict(ride.metrics_dict) for ride in ride_hub}


def create_ride_summary_dataframe() -> pd.DataFrame:
    """
    This function pulls and cleans the metadata for each ride.  The intended use of this DataFrame is to visualize
    trends over time This could be in the form of distance, average power, etc.
    """

    raw_df = pd.DataFrame([ride.metadata for ride in ride_hub])
    output_df = raw_df.copy()
    # Convert speed to MPH
    output_df.average_speed = output_df.average_speed.map(_convert_mps_to_mph)
    output_df.max_speed = output_df.average_speed.map(_convert_mps_to_mph)
    # Break out starting/ending latitude and longitude
    output_df['starting_latitude'] = output_df.start_latlng.map(lambda x: _grab_element_of_list_if_exists(x, 0))
    output_df['starting_longitude'] = output_df.start_latlng.map(lambda x: _grab_element_of_list_if_exists(x, 1))
    output_df['ending_latitude'] = output_df.end_latlng.map(lambda x: _grab_element_of_list_if_exists(x, 0))
    output_df['ending_longitude'] = output_df.end_latlng.map(lambda x: _grab_element_of_list_if_exists(x, 1))
    # Pull Athlete ID out from dictionary
    output_df['athlete_id'] = output_df.athlete.map(lambda x: x['id'])
    # Do the same for maps
    output_df['map_id'] = output_df.map.map(lambda x: x['id'])
    output_df['polyline'] = output_df.map.map(lambda x: x['summary_polyline'])
    # Convert to miles

    output_df.distance = output_df.distance.map(_convert_meters_to_miles)
    # Convert meters to feet
    output_df.total_elevation_gain = output_df.total_elevation_gain.map(_convert_meters_to_feet)
    output_df.elev_high = output_df.elev_high.map(_convert_meters_to_feet)
    output_df.elev_low = output_df.elev_low.map(_convert_meters_to_feet)
    # Address moving time
    output_df = output_df.rename(columns={'moving_time': 'moving_time_seconds'})
    output_df = output_df.rename(columns={'elapsed_time': 'elapsed_time_seconds'})
    output_df['moving_time'] = output_df.moving_time_seconds.map(_convert_total_seconds_to_HMS_format)
    output_df['elapsed_time'] = output_df.elapsed_time_seconds.map(_convert_total_seconds_to_HMS_format)

    # Add normalized power, IF and TSS
    output_df['normalized_power'] = output_df.id.map(create_normalized_power_dict())
    output_df['intensity_factor'] = output_df.normalized_power.map(lambda x: x / CURRENT_FTP)
    output_df['tss'] = output_df.apply(lambda x: _apply_training_stress_score(x), axis=1)

    # Return the output with the correct columns/order with the most recent being first
    return output_df[master_column_list].sort_values('start_date', ascending=False).drop_duplicates()
