"""
OAuth2 Client Credentials Flow Example

This example demonstrates how to implement the OAuth2 Client Credentials Flow
for service account (robot) authentication with the Planview ProjectPlace API.

This flow is used for application-to-application communication where no user
interaction is required.
"""

import requests
import requests.auth
from datetime import datetime, timedelta

# Replace these with your robot account credentials
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'


class OAuth2ClientCredentials:
    """
    A reusable class for managing OAuth2 Client Credentials authentication
    """

    def __init__(self, client_id, client_secret, api_endpoint=API_ENDPOINT):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_endpoint = api_endpoint
        self.access_token = None
        self.token_expires_at = None

    def get_access_token(self, force_refresh=False):
        """
        Get a valid access token, refreshing if necessary

        Args:
            force_refresh (bool): Force getting a new token even if current one is valid

        Returns:
            str: Valid access token
        """
        # Check if we have a valid token
        if not force_refresh and self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Request a new token
        print('Requesting new access token...')

        response = requests.post(
            f'{self.api_endpoint}/oauth2/access_token',
            data={
                'grant_type': 'client_credentials',
            },
            auth=requests.auth.HTTPBasicAuth(self.client_id, self.client_secret),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        response.raise_for_status()
        token_data = response.json()

        self.access_token = token_data['access_token']
        # Set expiration with a 5-minute buffer
        expires_in = token_data.get('expires', 2592000)  # Default 30 days
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

        print(f'✓ Access token obtained (expires in {expires_in} seconds)')

        return self.access_token

    def get_auth_headers(self):
        """
        Get headers for authenticated API requests

        Returns:
            dict: Headers with Authorization token
        """
        token = self.get_access_token()
        return {
            'Authorization': f'Bearer {token}'
        }

    def get(self, endpoint, **kwargs):
        """
        Make an authenticated GET request

        Args:
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests.get

        Returns:
            requests.Response: Response object
        """
        headers = kwargs.get('headers') or {}
        headers.update(self.get_auth_headers())
        kwargs['headers'] = headers
        return requests.get(f'{self.api_endpoint}{endpoint}', **kwargs)

    def post(self, endpoint, **kwargs):
        """
        Make an authenticated POST request

        Args:
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests.post

        Returns:
            requests.Response: Response object
        """
        headers = kwargs.get('headers') or {}
        headers.update(self.get_auth_headers())
        kwargs['headers'] = headers
        return requests.post(f'{self.api_endpoint}{endpoint}', **kwargs)

    def put(self, endpoint, **kwargs):
        """
        Make an authenticated PUT request

        Args:
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests.put

        Returns:
            requests.Response: Response object
        """
        headers = kwargs.get('headers') or {}
        headers.update(self.get_auth_headers())
        kwargs['headers'] = headers
        return requests.put(f'{self.api_endpoint}{endpoint}', **kwargs)

    def delete(self, endpoint, **kwargs):
        """
        Make an authenticated DELETE request

        Args:
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests.delete

        Returns:
            requests.Response: Response object
        """
        headers = kwargs.get('headers') or {}
        headers.update(self.get_auth_headers())
        kwargs['headers'] = headers
        return requests.delete(f'{self.api_endpoint}{endpoint}', **kwargs)


def example_basic_usage():
    """
    Example 1: Basic usage of client credentials flow
    """
    print('\n=== Example 1: Basic Token Request ===')

    # Method 1: Using Basic HTTP Authentication (recommended)
    response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data={
            'grant_type': 'client_credentials',
        },
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )

    response.raise_for_status()
    token_data = response.json()

    print(f'✓ Access token received')
    print(f'  Token type: {token_data["token_type"]}')
    print(f'  Access token: {token_data["access_token"][:20]}...')
    print(f'  Expires in: {token_data.get("expires", "N/A")} seconds')

    return token_data['access_token']


def example_alternative_method():
    """
    Example 2: Alternative method - passing credentials in request body
    """
    print('\n=== Example 2: Alternative Method (Body Parameters) ===')

    response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data={
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    response.raise_for_status()
    token_data = response.json()

    print(f'✓ Access token received via alternative method')

    return token_data['access_token']


def example_api_calls(access_token):
    """
    Example 3: Making API calls with the access token
    """
    print('\n=== Example 3: Making API Calls ===')

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Get account information
    print('\n--- Fetching Account Workspaces ---')
    response = requests.post(
        f'{API_ENDPOINT}/2/account/projects',
        json={
            'sort_by': '+creation_date',
            'filter': {
                'archive_status': [0]  # Only active workspaces
            },
            'limit': 5
        },
        headers=headers
    )

    response.raise_for_status()
    workspaces = response.json()

    print(f'✓ Found {len(workspaces)} workspace(s)')
    for ws in workspaces:
        print(f'  - {ws["name"]} (ID: {ws["id"]})')

    # Get robot user information
    print('\n--- Fetching Robot User Info ---')
    response = requests.get(
        f'{API_ENDPOINT}/1/user/me',
        headers=headers
    )

    response.raise_for_status()
    user_data = response.json()

    print(f'✓ Robot account details:')
    print(f'  - Name: {user_data.get("first_name")} {user_data.get("last_name")}')
    print(f'  - Email: {user_data.get("email")}')
    print(f'  - User ID: {user_data.get("id")}')
    print(f'  - Is Robot: {user_data.get("is_robot", False)}')


def example_reusable_client():
    """
    Example 4: Using the reusable OAuth2ClientCredentials class
    """
    print('\n=== Example 4: Using Reusable Client Class ===')

    # Create a client instance
    client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

    # The client automatically handles token management
    print('\n--- First API Call ---')
    response = client.get('/1/user/me')
    response.raise_for_status()
    user_data = response.json()
    print(f'✓ User: {user_data.get("email")}')

    print('\n--- Second API Call (reuses token) ---')
    response = client.post(
        '/2/account/projects',
        json={
            'limit': 3,
            'filter': {'archive_status': [0]}
        }
    )
    response.raise_for_status()
    workspaces = response.json()
    print(f'✓ Found {len(workspaces)} workspaces')

    print('\n--- Force Token Refresh ---')
    new_token = client.get_access_token(force_refresh=True)
    print(f'✓ New token: {new_token[:20]}...')


def example_error_handling():
    """
    Example 5: Proper error handling
    """
    print('\n=== Example 5: Error Handling ===')

    try:
        # Intentionally use invalid credentials
        response = requests.post(
            f'{API_ENDPOINT}/oauth2/access_token',
            data={'grant_type': 'client_credentials'},
            auth=requests.auth.HTTPBasicAuth('invalid', 'invalid')
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'✓ Caught authentication error: {e.response.status_code}')
        print(f'  Error message: {e.response.text}')

    # Test with valid credentials
    client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

    try:
        # Try to access a resource that doesn't exist
        response = client.get('/1/workspaces/999999999')
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'✓ Caught API error: {e.response.status_code}')
        if e.response.status_code == 404:
            print(f'  Resource not found or access denied')


def main():
    """
    Main function demonstrating OAuth2 Client Credentials Flow
    """
    print('==============================================')
    print('OAuth2 Client Credentials Flow Example')
    print('==============================================')
    print('\nThis flow is used for:')
    print('  - Robot/service account authentication')
    print('  - Application-to-application communication')
    print('  - Account-wide operations')
    print('\nNote: This requires a robot account set up')
    print('      by your organization administrator')
    print('==============================================\n')

    try:
        # Example 1: Basic token request
        access_token = example_basic_usage()

        # Example 2: Alternative method
        example_alternative_method()

        # Example 3: Making API calls
        example_api_calls(access_token)

        # Example 4: Using reusable client
        example_reusable_client()

        # Example 5: Error handling
        example_error_handling()

        print('\n==============================================')
        print('✓ All examples completed successfully!')
        print('==============================================')

    except requests.exceptions.HTTPError as e:
        print(f'\n❌ HTTP Error: {e.response.status_code}')
        print(f'Response: {e.response.text}')
        print('\nCommon issues:')
        print('  - Invalid CLIENT_ID or CLIENT_SECRET')
        print('  - Robot account not properly configured')
        print('  - Insufficient permissions')
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
