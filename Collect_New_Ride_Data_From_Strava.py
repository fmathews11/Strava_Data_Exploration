import json
from modules.api_functions import generate_access_token
from modules.create_logger import create_logger
from modules.objects.RideDataProcessor import RideDataProcessor
from modules.objects.RideHub import RideHub


with open('data/saved_strava_rides.json', 'rb') as file:
    saved_ride_hub = RideHub(*json.load(file))


def main() -> None:
    token = generate_access_token()
    headers = {'Authorization': f'Authorization: Bearer {token}'}
    processor = RideDataProcessor(token, headers, saved_ride_hub)
    processor.retrieve_and_process_new_ride_data()


if __name__ == '__main__':
    main()
