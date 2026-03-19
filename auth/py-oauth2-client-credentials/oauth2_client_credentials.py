"""
OAuth2 Client Credentials Flow Example

This example demonstrates how to implement the OAuth2 Client Credentials Flow
for service account (robot) authentication with the Planview ProjectPlace API.

This flow is used for application-to-application communication where no user
interaction is required.
"""

import requests
import requests.auth

# Replace these with your robot account credentials
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
SUBDOMAIN = 'REDACTED'  # e.g. 'mycompany'
API_ENDPOINT = f'https://{SUBDOMAIN}.projectplace.com'

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
        f'{API_ENDPOINT}/oauth2/access_token',
        data={
            'grant_type': 'client_credentials',
        },
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )
    access_token_response.raise_for_status()
    access_token = access_token_response.json()['access_token']


def fetch_projects():
    """
    Fetch the first 5 active workspaces from the account.
    """
    response = requests.post(
        f'{API_ENDPOINT}/2/account/projects',
        json={
            'sort_by': '+creation_date',
            'filter': {
                'archive_status': [0]  # Only active workspaces
            },
            'limit': 5
        },
        headers={'Authorization': f'Bearer {access_token}'}
    )
    response.raise_for_status()
    return response.json()


def main():
    print('OAuth2 Client Credentials Flow Example')
    print('=' * 40)

    # Get access token
    print('\nRequesting access token...')
    _ensure_access_token()
    print(f'✓ Access token received: {access_token[:20]}...')

    # Fetch projects
    print('\nFetching workspaces...')
    workspaces = fetch_projects()

    print(f'✓ Found {len(workspaces)} workspace(s):')
    for ws in workspaces:
        print(f'  - {ws["name"]} (ID: {ws["id"]})')


if __name__ == '__main__':
    main()
