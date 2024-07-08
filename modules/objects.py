from dataclasses import dataclass
from typing import Dict


# Internal use
def _validate_strava_ride(obj) -> None:
    if not isinstance(obj, StravaRide):
        raise ValueError(f"The input passed must be of type StravaRide.  Object passed was of type {type(obj)}")


@dataclass
class StravaRide:
    """Simple dataclass created to house ride information"""
    id: int
    metadata: Dict
    metrics_dict: Dict[str, list]

    def to_dict(self):
        """Method to return the data in a Python dictionary format"""
        return {"id": self.id,
                "metadata": self.metadata,
                "metrics_dict": self.metrics_dict}


class RideHub:
    """Class to house StravaRide objects"""
    _ride_list = []

    def __init__(self, *args):
        if args:
            self._ride_list.extend(args)

    def __str__(self):
        return f"RideHub(n_rides={len(self._ride_list)})"

    def __repr__(self):
        return self.__str__()

    def add_ride(self, ride_obj):
        """Add a ride to an existing list"""
        _validate_strava_ride(ride_obj)
        self._ride_list.append(ride_obj)

    def remove_ride(self, ride_id_to_remove):

        id_set = set([ride.id for ride in self._ride_list])

        if ride_id_to_remove not in id_set:
            raise ValueError(f"{ride_id_to_remove} is not contained in this RideHub")

        self._ride_list = [ride for ride in self._ride_list if ride_id_to_remove.id != ride_id_to_remove]

    @property
    def ride_list(self):
        """
        A "getter" method to access the ride list attribute. Using the @property decorator to not allow modification
        of the list.  This must be done via the `add_ride()` and `remove_ride()` class methods
        """
        return self._ride_list

    @property
    def ride_ids(self):
        """
        A "getter" method to access a list of ride IDs
        """
        return [i.id for i in self._ride_list]
