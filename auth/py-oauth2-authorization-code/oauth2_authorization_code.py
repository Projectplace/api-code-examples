"""
OAuth2 Authorization Code Flow Example

This example demonstrates how to implement the OAuth2 Authorization Code Flow
for user authentication with the Planview ProjectPlace API.

This flow is used when you need to access resources on behalf of a user.
"""

import random
import requests
import webbrowser
from urllib.parse import urlencode

# Replace these with your application credentials
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
SUBDOMAIN = 'REDACTED'  # e.g. 'mycompany'
REDIRECT_URI = 'https://oob'  # Must match your app settings
API_ENDPOINT = f'https://{SUBDOMAIN}.projectplace.com'


def get_authorization_code():
    """
    Opens browser for user authorization and prompts for the auth code.
    """
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': f'random_{random.randint(1000000, 10000000)}'
    }

    auth_url = f'{API_ENDPOINT}/oauth2/authorize?{urlencode(auth_params)}'

    print(f'Opening browser for authorization...')
    print(f'URL: {auth_url}')
    webbrowser.open(auth_url)

    return input('Enter the authorization code: ')


def exchange_code_for_tokens(code):
    """
    Exchange authorization code for access and refresh tokens.
    """
    response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
    )
    response.raise_for_status()
    return response.json()


def fetch_user_profile(access_token):
    """
    Fetch the current user's profile to verify the token works.
    """
    response = requests.get(
        f'{API_ENDPOINT}/1/user/me/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    response.raise_for_status()
    return response.json()


def main():
    print('OAuth2 Authorization Code Flow Example')
    print('=' * 40)

    # Step 1: Get authorization code
    print('\nStep 1: Get authorization code')
    code = get_authorization_code()
    print(f'✓ Authorization code received')

    # Step 2: Exchange code for tokens
    print('\nStep 2: Exchange code for tokens')
    tokens = exchange_code_for_tokens(code)
    print(f'✓ Access token received: {tokens["access_token"][:20]}...')
    print(f'  Expires in: {tokens["expires"]} seconds')

    # Step 3: Test API access
    print('\nStep 3: Test API access')
    user = fetch_user_profile(tokens['access_token'])
    print(f'✓ Logged in as: {user.get("first_name")} {user.get("last_name")}')
    print(f'  Email: {user.get("email")}')


if __name__ == '__main__':
    main()
