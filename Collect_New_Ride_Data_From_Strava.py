import requests
import json
from tqdm import tqdm
import time
import numpy as np
from modules.api_functions import generate_access_token, get_activity_data
from modules.create_logger import create_logger
from modules.objects.RideHub import RideHub
from modules.objects.StravaRide import StravaRide

logger = create_logger('RideStatusLogger', 'debug')
endpoint_suffix = ("/streams?keys=time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,"
                   "grade_smooth&key_by_type=true")

with open('data/saved_strava_rides.json', 'rb') as f:
    saved_ride_hub = RideHub(*json.load(f))


def main() -> None:
    global saved_ride_hub

    token = generate_access_token()
    headers = {'Authorization': f'Authorization: Bearer {token}'}

    all_activities = get_activity_data(token, params={'per_page': 200})
    ride_ids_with_power_meter_data = [i['id'] for i in all_activities if i.get('device_watts')]
    ride_ids_to_update = [i for i in ride_ids_with_power_meter_data if i not in saved_ride_hub]
    logger.info(f"{len(ride_ids_to_update)} rides to add to pre-existing ride hub")

    if not ride_ids_to_update:
        logger.info("No new rides to add")
        return

    for ride_id_to_update in tqdm(ride_ids_to_update):
        activity_stream_endpoint = f"https://www.strava.com/api/v3/activities/{ride_id_to_update}{endpoint_suffix}"
        response = requests.get(activity_stream_endpoint, headers=headers)

        ride_object = StravaRide(id=ride_id_to_update,
                                 metadata=[i for i in all_activities if i['id'] == ride_id_to_update][0],
                                 metrics_dict={key: array['data'] for key, array in response.json().items()})

        saved_ride_hub.add_ride(ride_object)
        time.sleep(np.random.randint(5, 30))

    with open('data/saved_strava_rides.json', 'w') as file:
        json.dump(saved_ride_hub.create_json_output(), file)
        logger.info(f"Successful write, {len(saved_ride_hub)} total rides with power data")
    return


if __name__ == '__main__':
    main()
