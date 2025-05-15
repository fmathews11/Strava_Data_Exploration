import json
import streamlit as st
from modules.api_functions import generate_access_token
from modules.objects.RideDataProcessor import RideDataProcessor
from modules.objects.RideHub import RideHub

with open('data/saved_strava_rides.json', 'rb') as file:
    saved_ride_hub = RideHub(*json.load(file))

st.set_page_config(page_title="Home Page", layout="centered")


def main():
    st.title("Frank's Ride Views")

    if st.button("Refresh Data"):
        token = generate_access_token()
        headers = {'Authorization': f'Authorization: Bearer {token}'}
        processor = RideDataProcessor(token, headers, saved_ride_hub)

        status_placeholder = st.empty()
        updated_count = processor.retrieve_and_process_new_ride_data(status_placeholder)
        if updated_count > 0:
            st.success(f"Data refreshed: {updated_count} new rides have been added.")
        else:
            st.info("No new rides to update.")


if __name__ == "__main__":
    main()
