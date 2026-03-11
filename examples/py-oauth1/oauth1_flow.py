"""
OAuth1 Authentication Example

This example demonstrates how to use OAuth1 authentication with the
Planview ProjectPlace API.

Note: OAuth1 is a legacy authentication method. For new integrations,
we recommend using OAuth2 (Authorization Code Flow or Client Credentials Flow).
"""

import oauth2
import requests
import webbrowser
import requests_oauthlib
from urllib.parse import parse_qs

# Replace these with your application credentials
APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'

# OAuth1 endpoints
API_ENDPOINT = 'https://api.projectplace.com'
REQUEST_TOKEN_URL = f'{API_ENDPOINT}/initiate'
AUTHORIZE_URL = f'{API_ENDPOINT}/authorize'
ACCESS_TOKEN_URL = f'{API_ENDPOINT}/token'


def get_request_token():
    """
    Step 1: Obtain a request token

    Returns:
        tuple: (oauth_token, oauth_token_secret)
    """
    print('=== Step 1: Get Request Token ===')

    consumer = oauth2.Consumer(APPLICATION_KEY, APPLICATION_SECRET)
    client = oauth2.Client(consumer)

    resp, content = client.request(REQUEST_TOKEN_URL, "GET")

    if resp['status'] != '200':
        raise Exception(f"Failed to get request token: {content}")

    request_token = dict(parse_qs(content.decode('utf-8')))
    oauth_token = request_token['oauth_token'][0]
    oauth_token_secret = request_token['oauth_token_secret'][0]

    print(f'✓ Request token obtained')
    print(f'  Token: {oauth_token[:20]}...')
    print(f'  Secret: {oauth_token_secret[:20]}...')

    return oauth_token, oauth_token_secret


def authorize_token(oauth_token):
    """
    Step 2: Redirect user to authorize the token

    Args:
        oauth_token (str): The request token

    Returns:
        str: OAuth verifier code
    """
    print('\n=== Step 2: Authorize Token ===')

    # Build authorization URL
    auth_url = f'{AUTHORIZE_URL}?oauth_token={oauth_token}'

    print(f'Opening browser for authorization...')
    print(f'URL: {auth_url}')

    # Open browser for user authorization
    webbrowser.open(auth_url)

    print('\nAfter authorizing the application in your browser,')
    print('you will see an OAuth verifier code.')
    oauth_verifier = input('Enter the OAuth verifier: ')

    if not oauth_verifier:
        raise Exception('OAuth verifier is required')

    print(f'✓ Verifier received: {oauth_verifier[:10]}...')

    return oauth_verifier


def get_access_token(oauth_token, oauth_token_secret, oauth_verifier):
    """
    Step 3: Exchange request token for access token

    Args:
        oauth_token (str): Request token
        oauth_token_secret (str): Request token secret
        oauth_verifier (str): Verifier code from authorization

    Returns:
        tuple: (access_token, access_token_secret)
    """
    print('\n=== Step 3: Get Access Token ===')

    consumer = oauth2.Consumer(APPLICATION_KEY, APPLICATION_SECRET)
    token = oauth2.Token(oauth_token, oauth_token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth2.Client(consumer, token)

    resp, content = client.request(ACCESS_TOKEN_URL, "GET")

    if resp['status'] != '200':
        raise Exception(f"Failed to get access token: {content}")

    access_token_data = dict(parse_qs(content.decode('utf-8')))
    access_token = access_token_data['oauth_token'][0]
    access_token_secret = access_token_data['oauth_token_secret'][0]

    print(f'✓ Access token obtained')
    print(f'  Token: {access_token[:20]}...')
    print(f'  Secret: {access_token_secret[:20]}...')

    return access_token, access_token_secret


def test_api_access(access_token, access_token_secret):
    """
    Step 4: Make API calls using the access token

    Args:
        access_token (str): OAuth1 access token
        access_token_secret (str): OAuth1 access token secret
    """
    print('\n=== Step 4: Test API Access ===')

    # Create OAuth1 session
    oauth1 = requests_oauthlib.OAuth1(
        client_key=APPLICATION_KEY,
        client_secret=APPLICATION_SECRET,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    # Test 1: Get user information
    print('\n--- Fetching User Information ---')
    response = requests.get(f'{API_ENDPOINT}/1/user/me', auth=oauth1)
    response.raise_for_status()
    user_data = response.json()

    print(f'✓ User information retrieved')
    print(f'  Name: {user_data.get("first_name")} {user_data.get("last_name")}')
    print(f'  Email: {user_data.get("email")}')
    print(f'  User ID: {user_data.get("id")}')

    # Test 2: Get user's workspaces
    print('\n--- Fetching Workspaces ---')
    response = requests.get(f'{API_ENDPOINT}/1/user/me/projects', auth=oauth1)
    response.raise_for_status()
    workspaces = response.json()

    print(f'✓ Found {len(workspaces)} workspace(s)')
    for ws in workspaces[:5]:  # Show first 5
        print(f'  - {ws["name"]} (ID: {ws["id"]})')

    return oauth1


def example_additional_api_calls(oauth1):
    """
    Additional examples of API calls using OAuth1

    Args:
        oauth1: OAuth1 session object
    """
    print('\n=== Additional API Examples ===')

    # Get a specific workspace's boards
    print('\n--- Example: Fetching Boards ---')

    # First, get workspaces to find one to work with
    response = requests.get(f'{API_ENDPOINT}/1/user/me/projects', auth=oauth1)
    workspaces = response.json()

    if workspaces:
        workspace_id = workspaces[0]['id']
        workspace_name = workspaces[0]['name']

        print(f'Getting boards for workspace: {workspace_name}')
        response = requests.get(
            f'{API_ENDPOINT}/1/projects/{workspace_id}/boards',
            auth=oauth1
        )

        if response.ok:
            boards = response.json()
            print(f'✓ Found {len(boards)} board(s)')
            for board in boards[:3]:  # Show first 3
                print(f'  - {board["name"]} (ID: {board["id"]})')
        else:
            print(f'Could not fetch boards: {response.status_code}')


def example_using_requests_oauthlib():
    """
    Alternative example using requests-oauthlib library directly
    This is useful when you already have access tokens
    """
    print('\n=== Alternative: Using requests-oauthlib Directly ===')
    print('If you already have access tokens, you can use them directly:')
    print('')
    print('```python')
    print('import requests')
    print('import requests_oauthlib')
    print('')
    print('oauth1 = requests_oauthlib.OAuth1(')
    print('    client_key=APPLICATION_KEY,')
    print('    client_secret=APPLICATION_SECRET,')
    print('    resource_owner_key=ACCESS_TOKEN,')
    print('    resource_owner_secret=ACCESS_TOKEN_SECRET')
    print(')')
    print('')
    print('response = requests.get(')
    print('    "https://api.projectplace.com/1/user/me",')
    print('    auth=oauth1')
    print(')')
    print('```')


def main():
    """
    Main function demonstrating complete OAuth1 flow
    """
    print('==============================================')
    print('OAuth1 Authentication Example')
    print('==============================================')
    print('\nNote: OAuth1 is a legacy authentication method.')
    print('For new integrations, consider using OAuth2.')
    print('')
    print('This example will:')
    print('1. Obtain a request token')
    print('2. Open browser for user authorization')
    print('3. Exchange for an access token')
    print('4. Make API calls with the access token')
    print('==============================================\n')

    try:
        # Step 1: Get request token
        oauth_token, oauth_token_secret = get_request_token()

        # Step 2: Authorize token
        oauth_verifier = authorize_token(oauth_token)

        # Step 3: Get access token
        access_token, access_token_secret = get_access_token(
            oauth_token,
            oauth_token_secret,
            oauth_verifier
        )

        # Step 4: Test API access
        oauth1_session = test_api_access(access_token, access_token_secret)

        # Additional examples
        example_additional_api_calls(oauth1_session)

        # Show how to use tokens directly
        example_using_requests_oauthlib()

        print('\n==============================================')
        print('✓ OAuth1 flow completed successfully!')
        print('==============================================')
        print('\nYour OAuth1 Credentials:')
        print(f'Application Key: {APPLICATION_KEY}')
        print(f'Application Secret: {APPLICATION_SECRET}')
        print(f'Access Token: {access_token}')
        print(f'Access Token Secret: {access_token_secret}')
        print('\nStore these credentials securely to use in your application.')
        print('OAuth1 tokens do not expire, but can be revoked by the user.')

    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
