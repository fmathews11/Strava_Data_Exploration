from datetime import datetime, timedelta
import json
from typing import Any
import numpy as np
import pandas as pd
from modules.objects.RideHub import RideHub
from modules.power_functions import calculate_normalized_power_from_metrics_dict, calculate_training_stress_score, \
    identify_heart_rate_zone
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

individual_ride_fields_outdoors = ['temp',
                                   'watts',
                                   'moving',
                                   'latitude',
                                   'longitude',
                                   'velocity_smooth',
                                   'grade_smooth',
                                   'cadence',
                                   'distance',
                                   'heartrate',
                                   'altitude',
                                   'time']

individual_ride_fields_indoors = ['temp',
                                  'watts',
                                  'moving',
                                  'velocity_smooth',
                                  'grade_smooth',
                                  'cadence',
                                  'distance',
                                  'heartrate',
                                  'hr_zone',
                                  'altitude',
                                  'time']

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

    # Convert start date to proper datetime format
    output_df.start_date = pd.to_datetime(output_df.start_date)
    # Return the output with the correct columns/order with the most recent being first
    return output_df[master_column_list].sort_values('start_date', ascending=False).drop_duplicates()


def create_individual_ride_metrics_dataframe(ride_id: int) -> pd.DataFrame:
    """Creates a dataframe of metrics for a given ride ID"""

    # Fail fast
    if not ride_hub.get_ride(ride_id):
        raise ValueError(f"Ride {ride_id} does not exist in the RideHub."
                         f"Call the ride_list() method to see available rides")

    output_df = pd.DataFrame(ride_hub[ride_id].metrics_dict)
    # Convert speed/Distance
    output_df.velocity_smooth = output_df.velocity_smooth.map(_convert_meters_to_feet)
    output_df.distance = output_df.distance.map(_convert_meters_to_miles)

    # Assign heart rate zones
    output_df['hr_zone'] = output_df.heartrate.map(identify_heart_rate_zone)
    # Determine whether it was an indoor or outdoor ride, Indoor trainer sessions have no 'latlng' field.
    is_outdoors = 'latlng' in output_df.columns
    if is_outdoors:
        output_df['latitude'] = output_df.latlng.map(lambda x: _grab_element_of_list_if_exists(x, 0))
        output_df['longitude'] = output_df.latlng.map(lambda x: _grab_element_of_list_if_exists(x, 1))
        return output_df[individual_ride_fields_outdoors]

    return output_df[individual_ride_fields_indoors]


def get_daily_tss_score_array() -> np.ndarray:
    """This function computes the daily TSS (training stress score) for the last 43 days.
    Days with no training are filled in with a value of zero.

    Each value in the returned array represents the daily TSS for that day. Value zero represents today minus 43
    days, and value 43 represents today.  Any days with no training receive a value of zero.
    """
    # Get today, subtract 43 days.  Only 42 will be shown, but we need 43 days back to calculate the TSB for day 1
    cutoff_date = datetime.today() - timedelta(days=43)
    summary_df = create_ride_summary_dataframe()
    target_df = summary_df.loc[summary_df.start_date >= str(cutoff_date)][['start_date', 'tss']].set_index(
        'start_date').copy()
    target_df.index = pd.DatetimeIndex(target_df.index)
    target_df.index = pd.DatetimeIndex(target_df.index.strftime('%m/%d/%Y'))
    target_df = target_df.groupby('start_date').tss.sum().copy()
    start_date, end_date = target_df.index.min(), target_df.index.max()
    date_range_to_apply = pd.date_range(start_date, end_date)
    target_df = target_df.reindex(date_range_to_apply, fill_value=0).reset_index().copy()
    return target_df.tss.to_numpy()
