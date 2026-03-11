**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# OAuth2 Authorization Code Flow Example

This example demonstrates how to implement the OAuth2 Authorization Code Flow for authenticating users with the Planview ProjectPlace API.

## When to Use This Flow

Use the **Authorization Code Flow** when:
- Your application needs to access resources **on behalf of a user**
- You need the user to authorize your application
- You're building a web application, mobile app, or desktop application
- You want to maintain long-term access using refresh tokens

## Overview

The OAuth2 Authorization Code Flow consists of these steps:

1. **Redirect user to authorization page** - User authorizes your application
2. **Receive authorization code** - User is redirected back with a code
3. **Exchange code for tokens** - Get access token and refresh token
4. **Use access token** - Make API calls on behalf of the user
5. **Refresh token** - Get new access tokens without user interaction

## Token Lifetimes

- **Access Token**: Valid for **30 days**
- **Refresh Token**: Valid for **120 days**

As long as you refresh your access token within 120 days, you can maintain indefinite access without requiring the user to re-authorize.

## Prerequisites

### 1. Register Your Application

Before you can use OAuth2, you must register your application in ProjectPlace:

1. Log in to ProjectPlace
2. Go to **User Settings** → **Developer** → **Applications**
3. Create a new application
4. Note your **Client ID** (Application Key) and **Client Secret**
5. Set your **Redirect URI** (e.g., `http://localhost:8080/callback` for local testing)

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

The required package is:
- `requests` - For making HTTP requests

## Configuration

Edit the script and replace these values:

```python
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
REDIRECT_URI = 'http://localhost:8080/callback'  # Must match your app settings
```

**Important**: The `REDIRECT_URI` must exactly match the redirect URI configured in your application settings in ProjectPlace.

## Usage

### Running the Example

```bash
python oauth2_authorization_code.py
```

### What Happens

1. The script starts a local HTTP server on port 8080
2. Your web browser opens to the ProjectPlace authorization page
3. You log in and authorize the application
4. ProjectPlace redirects back to the local server with an authorization code
5. The script exchanges the code for access and refresh tokens
6. The script demonstrates making API calls with the access token
7. The script demonstrates refreshing the access token

### Example Output

```
==============================================
OAuth2 Authorization Code Flow Example
==============================================

=== Step 1: Get Authorization Code ===
Opening browser to authorize application...
Waiting for authorization...
✓ Authorization code received

=== Step 2: Exchange Code for Tokens ===
✓ Access token received
  - Token type: Bearer
  - Expires in: 2592000 seconds (30.0 days)
  - Access token: a1b2c3d4e5f6g7h8i9j0...
  - Refresh token: z9y8x7w6v5u4t3s2r1q0...

=== Step 4: Test API Access ===
✓ API access successful!
  - User: John Doe
  - Email: john.doe@example.com
  - User ID: 12345

=== Step 3: Refresh Access Token ===
✓ New access token received
  - New access token: k1l2m3n4o5p6q7r8s9t0...
  - New refresh token: p0o9i8u7y6t5r4e3w2q1...

✓ OAuth2 flow completed successfully!
```

## Using the Tokens in Your Application

### Making API Calls with Access Token

Once you have an access token, you can make API calls in two ways:

**Method 1: Authorization Header (Recommended)**

```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(
    'https://api.projectplace.com/1/user/me',
    headers=headers
)
```

**Method 2: Query Parameter**

```python
response = requests.get(
    f'https://api.projectplace.com/1/user/me?access_token={access_token}'
)
```

### Refreshing Access Tokens

When your access token expires (after 30 days), use the refresh token to get a new one:

```python
import requests

refresh_data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
}

response = requests.post(
    'https://api.projectplace.com/oauth2/access_token',
    data=refresh_data,
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)

tokens = response.json()
new_access_token = tokens['access_token']
new_refresh_token = tokens['refresh_token']
```

**Important**: Both the access token AND refresh token are replaced when you refresh. You must store the new refresh token.

## Security Best Practices

1. **Never commit credentials** - Don't commit your `CLIENT_ID` and `CLIENT_SECRET` to version control
2. **Use environment variables** - Store credentials in environment variables or secure configuration files
3. **Use HTTPS in production** - Always use HTTPS for your redirect URI in production
4. **Validate state parameter** - Use the `state` parameter to prevent CSRF attacks
5. **Store tokens securely** - Never store tokens in plain text; use secure storage mechanisms
6. **Use HTTPS redirect URIs** - In production, your redirect URI should use HTTPS

## Troubleshooting

### "Redirect URI mismatch" error

Make sure the `REDIRECT_URI` in your code exactly matches the one configured in your application settings.

### "Port already in use" error

The callback server uses port 8080. If this port is in use, you can:
- Stop the process using port 8080
- Modify the script to use a different port (update both the server and REDIRECT_URI)

### Browser doesn't open

If the browser doesn't open automatically, copy the URL from the console and paste it into your browser manually.

### "Invalid client" error

Check that your `CLIENT_ID` and `CLIENT_SECRET` are correct.

## API Documentation

For complete API documentation, visit:
- [OAuth2 Documentation](https://api.projectplace.com/apidocs#articles/pageOAuth2.html)
- [API Reference](https://api.projectplace.com/apidocs)

## Related Examples

- **OAuth2 Client Credentials Flow** - For robot/service accounts
- **OAuth1 Flow** - Legacy authentication method

## Support

For more information about Planview ProjectPlace APIs:
- [Success Center](https://success.planview.com/Planview_ProjectPlace)
- [API Code Examples Repository](https://github.com/Projectplace/api-code-examples)

