import requests

from global_variables import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN

token_auth_url = 'https://www.strava.com/oauth/token'


def generate_access_token() -> str:

    """Uses the client ID, secret, and authorization-specific refresh token to generate a temporary
    access token"""

    param_dict = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': "refresh_token",
        'f': 'json'}

    response = requests.post(url=token_auth_url, params=param_dict)

    if response.status_code != 200:
        print(response.text)
        raise ValueError(f"Response status code was {response.status_code}")

    return response.json()['access_token']
