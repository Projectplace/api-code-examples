"""
OAuth2 Authorization Code Flow Example

This example demonstrates how to implement the OAuth2 Authorization Code Flow
for user authentication with the Planview ProjectPlace API.

This flow is used when you need to access resources on behalf of a user.
"""

import time
import requests
import threading
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

# Replace these with your application credentials
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
REDIRECT_URI = 'http://localhost:8080/callback'  # Must match your app settings
API_ENDPOINT = 'https://api.projectplace.com'

# Global variables to store the authorization result
authorization_code = None
authorization_error = None
auth_server = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive the OAuth callback"""

    def do_GET(self):
        global authorization_code

        # Parse the URL path and query parameters
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        # Only process requests to the callback path
        if parsed_url.path != '/callback':
            # Ignore unrelated requests (e.g., /favicon.ico)
            self.send_response(404)
            self.end_headers()
            return

        if 'code' in query:
            authorization_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <body>
                        <h1>Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                </html>
            """)
            # Shutdown the server after receiving a valid authorization code
            threading.Thread(target=self.server.shutdown).start()
        elif 'error' in query:
            global authorization_error
            error = query['error'][0]
            error_description = query.get('error_description', [''])[0]
            # Store the error for the main thread
            authorization_error = {
                'error': error,
                'description': error_description
            }
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_msg = f"{error}: {error_description}" if error_description else error
            self.wfile.write(f"""
                <html>
                    <body>
                        <h1>Authorization Failed</h1>
                        <p>Error: {error_msg}</p>
                    </body>
                </html>
            """.encode())
            # Shutdown the server after receiving an error
            threading.Thread(target=self.server.shutdown).start()
        else:
            # Callback path but missing required parameters
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <body>
                        <h1>Invalid Request</h1>
                        <p>Missing authorization code or error parameter.</p>
                    </body>
                </html>
            """)

    def log_message(self, format, *args):
        # Suppress log messages
        pass


def start_callback_server():
    """Start a local HTTP server to receive the OAuth callback"""
    global auth_server
    auth_server = HTTPServer(('localhost', 8080), CallbackHandler)
    auth_server.serve_forever()


def get_authorization_code():
    """
    Step 1: Redirect user to authorization page
    Opens a browser window for the user to authorize the application
    """
    global authorization_code

    # Start the callback server in a background thread
    server_thread = threading.Thread(target=start_callback_server)
    server_thread.daemon = True
    server_thread.start()

    # Build the authorization URL
    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'state': 'random_state_string'  # Should be random for security
    }

    auth_url = f'{API_ENDPOINT}/oauth2/authorize?{urlencode(auth_params)}'

    print('\n=== Step 1: Get Authorization Code ===')
    print(f'Opening browser to authorize application...')
    print(f'URL: {auth_url}')

    # Open the browser
    webbrowser.open(auth_url)

    # Wait for the callback
    print('Waiting for authorization...')
    timeout = 120  # 2 minutes timeout
    start_time = time.time()

    while authorization_code is None and authorization_error is None and (time.time() - start_time) < timeout:
        time.sleep(0.5)

    # Check for error first
    if authorization_error is not None:
        error_msg = authorization_error['error']
        if authorization_error['description']:
            error_msg += f": {authorization_error['description']}"
        raise Exception(f'Authorization failed - {error_msg}')

    if authorization_code is None:
        raise Exception('Authorization timed out')

    print(f'✓ Authorization code received')
    return authorization_code


def exchange_code_for_tokens(code):
    """
    Step 2: Exchange authorization code for access token and refresh token
    """
    print('\n=== Step 2: Exchange Code for Tokens ===')

    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    response.raise_for_status()
    tokens = response.json()

    print(f'✓ Access token received')
    print(f'  - Token type: {tokens["token_type"]}')
    print(f'  - Expires in: {tokens["expires"]} seconds ({tokens["expires"] / 86400:.1f} days)')
    print(f'  - Access token: {tokens["access_token"][:20]}...')
    print(f'  - Refresh token: {tokens["refresh_token"][:20]}...')

    return tokens


def refresh_access_token(refresh_token):
    """
    Step 3: Refresh access token using refresh token
    This allows you to get a new access token without user interaction
    """
    print('\n=== Step 3: Refresh Access Token ===')

    refresh_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data=refresh_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    response.raise_for_status()
    tokens = response.json()

    print(f'✓ New access token received')
    print(f'  - New access token: {tokens["access_token"][:20]}...')
    print(f'  - New refresh token: {tokens["refresh_token"][:20]}...')

    return tokens


def test_api_access(access_token):
    """
    Step 4: Use the access token to make API calls
    Tests the access token by fetching user information
    """
    print('\n=== Step 4: Test API Access ===')

    # Method 1: Using Authorization header (recommended)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        f'{API_ENDPOINT}/1/user/me',
        headers=headers
    )

    response.raise_for_status()
    user_data = response.json()

    print(f'✓ API access successful!')
    print(f'  - User: {user_data.get("first_name")} {user_data.get("last_name")}')
    print(f'  - Email: {user_data.get("email")}')
    print(f'  - User ID: {user_data.get("id")}')

    # Method 2: Using query parameter (alternative)
    # response = requests.get(f'{API_ENDPOINT}/1/user/me?access_token={access_token}')

    return user_data


def main():
    """
    Main function demonstrating the complete OAuth2 Authorization Code Flow
    """
    print('==============================================')
    print('OAuth2 Authorization Code Flow Example')
    print('==============================================')
    print('\nThis example will:')
    print('1. Open a browser for you to authorize the app')
    print('2. Exchange the authorization code for tokens')
    print('3. Demonstrate refreshing the access token')
    print('4. Make a test API call')
    print('\nNote: Make sure your REDIRECT_URI matches your')
    print('      application settings in ProjectPlace')
    print('==============================================\n')

    try:
        # Step 1: Get authorization code
        code = get_authorization_code()

        # Step 2: Exchange code for tokens
        tokens = exchange_code_for_tokens(code)
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']

        # Step 3: Test API access
        test_api_access(access_token)

        # Step 4: Demonstrate token refresh
        print('\n--- Demonstrating Token Refresh ---')
        new_tokens = refresh_access_token(refresh_token)

        # Test with new token
        test_api_access(new_tokens['access_token'])

        print('\n==============================================')
        print('✓ OAuth2 flow completed successfully!')
        print('==============================================')
        print('\nToken Information:')
        print(f'Access Token: {new_tokens["access_token"]}')
        print(f'Refresh Token: {new_tokens["refresh_token"]}')
        print(f'Expires in: {new_tokens["expires"]} seconds')
        print('\nStore these tokens securely to use in your application.')
        print('Use the refresh token to get new access tokens when needed.')

    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
