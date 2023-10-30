import gzip
import os
import math
import requests
import requests.auth
from datetime import datetime

CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
ODATA_BASE_URL = 'https://odata3.projectplace.com'
ACCESS_TOKEN_URL = 'https://api.projectplace.com/oauth2/access_token'
ODATA_ENDPOINTS = {
    'pm': 'Workspace data',
    'am': 'Account data',
    'portfolio': 'Portfolio data'
}

access_token = None


def _ensure_access_token():
    """
    We ask for a new access token on every script run - in normal circumstances you can hold on to an access
    token for longer than that.

    This function uses the client credentials flow which only works for robot accounts since it is intended for
    application-to-application communication. So the client_id and client_secret needs to belong to a robot and the
    resulting access token will also belong to the robot.
    """
    global access_token
    access_token_response = requests.post(
        ACCESS_TOKEN_URL,
        data={
            'grant_type': 'client_credentials',
        },
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )
    access_token_response.raise_for_status()
    access_token = access_token_response.json()['access_token']


def _prompt_endpoint():
    """
    Displays a prompt to the user - asking them to select an endpoint.
    """
    print('The following ODATA collections are available')
    _valid_choices = [str(_i + 1) for _i in range(len(ODATA_ENDPOINTS))]
    for _i, endpoint in enumerate(ODATA_ENDPOINTS):
        print(f' {_i + 1}. {ODATA_ENDPOINTS[endpoint]}')

    choice = input(f'Which would you like to investigate? ({", ".join(_valid_choices)}): ')

    if choice not in _valid_choices:
        print(f'You need to pick one of {", ".join(_valid_choices)}, aborting.')
        exit()

    return list(ODATA_ENDPOINTS.keys())[int(choice) - 1]


def _pick_entity_set(valid_entity_sets):
    """
    Displays a prompt to the user asking them to select an entity set within an endpoint
    """
    choice = input('Which entity set would you like to download? ')
    _valid_choices = [str(_i + 1) for _i in range(len(valid_entity_sets))]
    if choice not in _valid_choices:
        print(f'Invalid choice, pick from: {", ".join(_valid_choices)}')
        return _pick_entity_set(valid_entity_sets)

    return valid_entity_sets[int(choice) - 1]


def _show_available_entity_sets(odata_endpoint):
    """
    Shows which entity sets are available in the OData endpoint
    """
    response = requests.get(
        f'{ODATA_BASE_URL}/{odata_endpoint}'  # No authentication is necessary for discovery
    )
    response.raise_for_status()

    print(f'\nThe following entity sets are available for {ODATA_ENDPOINTS[odata_endpoint]}:')

    valid_entity_sets = [entity_set['name'] for entity_set in response.json()['value']]
    for _i, entity_set in enumerate(valid_entity_sets):
        print(f'{_i + 1}. {entity_set}')

    return _pick_entity_set(valid_entity_sets)


def _convert_size(size_bytes):
    """
    A simple utility function to display data sizes in a more human friendly manner.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def _download_entities(odata_endpoint, entity_set):
    """
    Progressively downloads all entities in a specific entity set (such as AccountWorkspaces) from a specific odata
    endpoint (such as "am").

    The contents are saved in a gzipped file.
    """
    url = f'{ODATA_BASE_URL}/{odata_endpoint}/{entity_set}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    file_name = f'{odata_endpoint}_{entity_set}_{datetime.now().date().isoformat()}.json.gz'
    size_downloaded = 0
    chunk_size = 102400  # 100 kB per pop
    print(f'Downloading {odata_endpoint}/{entity_set} please wait...          ', end='\r')
    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()
        with gzip.open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                size_downloaded += len(chunk)
                print(f'Downloading {odata_endpoint}/{entity_set} please wait... {_convert_size(size_downloaded)}'
                      f'          ', end='\r', flush=True)
                f.write(chunk)

    file_size = _convert_size(os.stat(file_name).st_size)

    print(f'Done! Downloaded {_convert_size(size_downloaded)} to {file_name} (Final file size: {file_size})')


def consume_odata():
    """ Entry point function """
    _ensure_access_token()
    odata_endpoint = _prompt_endpoint()
    entity_set = _show_available_entity_sets(odata_endpoint)
    _download_entities(odata_endpoint, entity_set)


if __name__ == '__main__':
    consume_odata()
