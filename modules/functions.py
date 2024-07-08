import requests
from global_variables import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

token_auth_url = 'https://www.strava.com/oauth/token'
activities_endpoint = "https://www.strava.com/api/v3/athlete/activities"

token_param_dict = {'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'refresh_token': REFRESH_TOKEN,
                    'grant_type': "refresh_token",
                    'f': 'json'}


# Internal use
def _validate_status_code(response_object: requests.models.Response):
    """Quick function to validate status code"""
    if response_object.status_code != 200:
        print(response_object.text)
        raise ValueError(f"Response status code was {response_object.status_code}")


def generate_access_token() -> str:
    """Uses the client ID, secret, and authorization-specific refresh token to generate a temporary
    access token"""

    response = requests.post(url=token_auth_url, params=token_param_dict)
    _validate_status_code(response_object=response)
    return response.json()['access_token']


def get_activity_data(access_token: str, params: dict = None) -> dict:
    """
    Returns a dictionary (response.json()) representing the user's 30 most recent activities
    """
    headers = {'Authorization': f'Authorization: Bearer {access_token}'}
    if not params:
        response = requests.get(activities_endpoint, headers=headers)
    else:
        response = requests.get(activities_endpoint, headers=headers, params=params)
    _validate_status_code(response_object=response)
    return response.json()
