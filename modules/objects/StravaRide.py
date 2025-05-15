from dataclasses import dataclass
from typing import Dict


@dataclass
class StravaRide:
    """
    Simple dataclass created to house ride information
    """

    id: int
    metadata: Dict
    metrics_dict: Dict[str, list]

    def to_dict(self):
        """
        Method to return the data in a Python dictionary format
        """

        return {"id": self.id,
                "metadata": self.metadata,
                "metrics_dict": self.metrics_dict}

    @classmethod
    def from_dict(cls, input_dict: dict) -> 'StravaRide':
        """
        Class method to create a StravaRide from a dictionary which contain the necessary keys
        """

        if any(i not in input_dict.keys() for i in ['id', 'metadata', 'metrics_dict']):
            raise AttributeError("Each of 'id','metadata','metrics_dict' must be present in dictionary keys")
        return cls(id=input_dict['id'], metadata=input_dict['metadata'], metrics_dict=input_dict['metrics_dict'])
