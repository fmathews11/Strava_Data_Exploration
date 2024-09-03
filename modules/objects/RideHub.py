from typing import Union
from modules.objects.Base import RideHubBase, _validate_strava_ride, StravaRide


class RideHub(RideHubBase):
    """
    Class to house StravaRide objects.
    The data will be pulled in and written out as JSON files, but this object was created to more easily interact
    with the data
    """

    def add_ride(self, ride_obj) -> None:
        """
        Add a ride to an existing list
        """

        _validate_strava_ride(ride_obj)
        self._ride_list.append(ride_obj)

    def remove_ride(self, ride_to_remove):
        """
        Removes a ride from the internal ride list
        """
        self._ride_list = [ride_to_keep for ride_to_keep in self._ride_list if ride_to_keep.id != ride_to_remove.id]

    def remove_ride_by_id(self, ride_id_to_remove):
        """
        Removes a ride from the internal ride list based on ID
        """
        if ride_id_to_remove not in self.ride_ids:
            raise ValueError(f"Ride {ride_id_to_remove} is not in this RideHub object")

        self._ride_list = [ride_to_keep for ride_to_keep in self._ride_list if ride_to_keep.id != ride_id_to_remove]

    def create_json_output(self) -> list[dict]:
        """
        Converts a series of StravaRide objects to one list of dictionaries for writing JSON
        files
        """

        return [ride.to_dict() for ride in self._ride_list]

    def get_ride(self, ride_id: int) -> Union[StravaRide, None]:
        """
        Mimicking the Python dictionary .get() method.
        Returning None if the ride_id is not found rather than raising an error
        """
        return self.__getitem__(ride_id=ride_id) if ride_id in self.ride_ids else None
