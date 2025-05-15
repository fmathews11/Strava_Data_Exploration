from abc import ABC
from modules.objects.StravaRide import StravaRide


# Internal use
def validate_strava_ride(obj) -> None:
    if not isinstance(obj, StravaRide):
        raise ValueError(f"The input passed must be of type StravaRide.  Object passed was of type {type(obj)}")


class RideHubBase(ABC):
    _ride_list = []

    def __init__(self, *args):

        for sub_dict in args:

            if sub_dict['id'] in self.ride_ids:
                continue

            temp_ride_object = StravaRide(sub_dict['id'],
                                          metadata=sub_dict['metadata'],
                                          metrics_dict=sub_dict['metrics_dict'])
            self._ride_list.append(temp_ride_object)

    def __str__(self):
        return f"RideHub(n_rides={len(self._ride_list)})"

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self._ride_list)

    def __iter__(self):
        self._pointer = 0
        return self

    def __next__(self):
        """
        Guide for iteration
        """
        if self._pointer > len(self._ride_list) - 1:
            raise StopIteration
        result = self._ride_list[self._pointer]
        self._pointer += 1
        return result

    def __contains__(self, ride_id: int):
        """
        Returns True if user-passed ID is an ID in the ride list
        """
        return ride_id in self.ride_ids

    def __getitem__(self, ride_id):
        if ride_id not in self.ride_ids:
            raise ValueError(f"{ride_id} does not exist")
        return [i for i in self._ride_list if i.id == ride_id][0]

    @property
    def ride_ids(self):
        """
        A "getter" method to access a list of ride IDs
        """

        return [i.id for i in self._ride_list]

    @property
    def ride_list(self):
        """
        A "getter" method to access the ride list attribute. Using the @property decorator to not allow modification
        of the list.  This must be done via the `add_ride()` and `remove_ride()` class methods
        """

        return self._ride_list

