import json
import time
import numpy as np
import requests
from tqdm import tqdm
from global_variables import CURRENT_FTP
from modules.api_functions import get_activity_data
from modules.create_logger import create_logger
from modules.objects.RideHub import RideHub
from modules.objects.StravaRide import StravaRide
from modules.power_functions import create_individual_ride_power_curve_array

ENDPOINT_SUFFIX = ("/streams?keys=time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,"
                   "grade_smooth&key_by_type=true")

logger = create_logger('RideStatusLogger', 'debug')


class RideDataProcessor:
    """
    Class for processing ride data and updating a pre-existing ride hub with new rides that contain power meter data.

    Methods:

        update_ride_data(self):
            Fetches data of all activities and updates the ride hub with new rides containing power meter data.

        Process_single_ride(self, ride_id: int, all_activities: list):
            Processes a single ride by fetching its detailed data and adding it to the ride hub.

        Save_ride_hub_to_file(self):
            Saves the current state of the ride hub to a JSON file.
    """

    def __init__(self, token: str, headers: dict, ride_hub: RideHub):
        self.token = token
        self.headers = headers
        self.ride_hub = ride_hub

    def retrieve_and_process_new_ride_data(self, streamlit_status_placeholder=None) -> int:
        """
        Retrieve and process new ride data that have power meter data available. Optionally
        provides status updates through a placeholder widget and saves updated ride hub
        data upon completion.

        Parameters
        ----------
        streamlit_status_placeholder : A streamlit empty object
            A placeholder for updating status messages, primarily used for live status
            updates in a Streamlit application.

        Returns
        -------
        int
            The number of new rides processed and added to the ride hub.  This is for surfacing
            in Streamlit
        """
        all_activities = get_activity_data(self.token, params={'per_page': 200})
        ride_ids_with_power_meter_data = [activity['id'] for activity in all_activities if activity.get('device_watts')]
        new_ride_ids = [ride_id for ride_id in ride_ids_with_power_meter_data if ride_id not in self.ride_hub]

        logger.info(f"{len(new_ride_ids)} rides to add to pre-existing ride hub")
        if not new_ride_ids:
            if streamlit_status_placeholder:
                streamlit_status_placeholder.info("No new rides to add.")
            return 0

        total_new_rides = len(new_ride_ids)

        # Process each ride and update the placeholder
        for idx, ride_id in enumerate(tqdm(new_ride_ids), start=1):
            self.process_single_ride(ride_id, all_activities)

            # Streamlit portion
            if streamlit_status_placeholder:
                streamlit_status_placeholder.info(f"Processing ride {idx} of {total_new_rides}...")

            time.sleep(np.random.randint(5, 8))

        # Save
        self._save_ride_hub_to_file()
        if streamlit_status_placeholder:
            streamlit_status_placeholder.success(f"Processed {total_new_rides} rides successfully!")

        return total_new_rides

    def process_single_ride(self, ride_id: int, all_activities: list[dict]) -> None:
        """
        Processes a single ride by fetching the activity data and metrics from the Strava API, creating a StravaRide
        object, and adding it to the ride hub.

        Arguments:
        ride_id (int): The unique identifier for the ride.
        all_activities (list): A list containing metadata for all activities.
        """
        activity_stream_endpoint = f"https://www.strava.com/api/v3/activities/{ride_id}{ENDPOINT_SUFFIX}"
        response = requests.get(activity_stream_endpoint, headers=self.headers)

        activity_data = next(activity for activity in all_activities if activity['id'] == ride_id)

        ride_object = StravaRide(
            id=ride_id,
            metadata=activity_data,
            metrics_dict={key: array['data'] for key, array in response.json().items()}
        )

        self.ride_hub.add_ride(ride_object)
        power_curve = create_individual_ride_power_curve_array(self.ride_hub, ride_id)
        ride_object.metrics_dict['power_curve'] = list(power_curve)
        ride_object.metadata['ftp'] = CURRENT_FTP

    def _save_ride_hub_to_file(self) -> None:
        """
        Saves the current ride hub to a file in JSON format.
        """
        with open('data/saved_strava_rides.json', 'w') as file:
            json.dump(self.ride_hub.create_json_output(), file)
            logger.info(f"Successful write, {len(self.ride_hub)} total rides with power data")
