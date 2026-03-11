**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# OAuth2 Client Credentials Flow Example

This example demonstrates how to implement the OAuth2 Client Credentials Flow for robot/service account authentication with the Planview ProjectPlace API.

## When to Use This Flow

Use the **Client Credentials Flow** when:
- Your application needs **account-wide access** (not on behalf of a specific user)
- You're using a **robot/service account**
- You're building server-to-server integrations
- No user interaction is required
- You need automated, programmatic access to your organization's data

## Overview

The Client Credentials Flow is simpler than the Authorization Code Flow:

1. **Request access token** - Exchange client credentials for an access token
2. **Use access token** - Make API calls with the token
3. **Request new token when needed** - No refresh token is needed; just request a new access token

## Key Differences from Authorization Code Flow

| Feature | Client Credentials | Authorization Code |
|---------|-------------------|-------------------|
| User interaction | None required | User must authorize |
| Token lifetime | 30 days | 30 days (access) / 120 days (refresh) |
| Refresh token | Not provided | Provided |
| Use case | Service accounts | User accounts |
| Scope | Account-wide | User-specific |

## Prerequisites

### 1. Set Up Robot Account

Before you can use this flow, your **organization administrator** must:

1. Log in to ProjectPlace as an account administrator
2. Go to **Account administration** → **Integration settings**
3. Create a new robot user
4. Generate OAuth2 credentials for the robot
5. Provide you with the **Client ID** and **Client Secret**

For detailed instructions, see: [How to Generate a Robot Token](https://success.planview.com/Planview_ProjectPlace/Integrations/Integrate_with_Planview_Hub%2F%2FViz_(Beta))

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

The required package is:
- `requests` - For making HTTP requests

## Configuration

Edit the script and replace these values:

```python
CLIENT_ID = 'your_robot_client_id_here'
CLIENT_SECRET = 'your_robot_client_secret_here'
```

**Security Note**: Never commit these credentials to version control. Use environment variables or secure configuration management.

## Usage

### Running the Example

```bash
python oauth2_client_credentials.py
```

The script demonstrates five examples:
1. Basic token request using HTTP Basic Authentication
2. Alternative method using body parameters
3. Making API calls with the access token
4. Using a reusable client class
5. Proper error handling

### Example Output

```
==============================================
OAuth2 Client Credentials Flow Example
==============================================

=== Example 1: Basic Token Request ===
Requesting new access token...
✓ Access token obtained (expires in 2592000 seconds)
✓ Access token received
  Token type: Bearer
  Access token: a1b2c3d4e5f6g7h8i9j0...
  Expires in: 2592000 seconds

=== Example 3: Making API Calls ===

--- Fetching Account Workspaces ---
✓ Found 5 workspace(s)
  - Project Alpha (ID: 12345)
  - Marketing Campaign (ID: 12346)
  - IT Infrastructure (ID: 12347)

--- Fetching Robot User Info ---
✓ Robot account details:
  - Name: API Robot
  - Email: api.robot@example.com
  - User ID: 98765
  - Is Robot: True

✓ All examples completed successfully!
```

## Authentication Methods

### Method 1: HTTP Basic Authentication (Recommended)

```python
import requests
import requests.auth

response = requests.post(
    'https://api.projectplace.com/oauth2/access_token',
    data={
        'grant_type': 'client_credentials',
    },
    auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
)

token = response.json()['access_token']
```

### Method 2: Body Parameters

```python
import requests

response = requests.post(
    'https://api.projectplace.com/oauth2/access_token',
    data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    },
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)

token = response.json()['access_token']
```

## Using the Access Token

### Making API Calls

Once you have an access token, include it in the Authorization header:

```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}'
}

# Get workspaces
response = requests.post(
    'https://api.projectplace.com/2/account/projects',
    json={
        'sort_by': '+creation_date',
        'filter': {
            'archive_status': [0]  # Active workspaces only
        },
        'limit': 10
    },
    headers=headers
)

workspaces = response.json()
```

### Reusable Client Class

The example includes a reusable `OAuth2ClientCredentials` class that:
- Automatically manages token lifecycle
- Handles token expiration
- Provides convenient methods for GET, POST, PUT, DELETE requests

```python
from oauth2_client_credentials import OAuth2ClientCredentials

# Create client
client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

# Make requests (token is handled automatically)
response = client.get('/1/user/me')
user_data = response.json()

response = client.post('/2/account/projects', json={'limit': 10})
workspaces = response.json()
```

## Token Management

### Token Expiration

- Access tokens expire after **30 days** (2,592,000 seconds)
- No refresh token is provided
- To get a new token, simply repeat the client credentials flow

### When to Request New Tokens

The example client class automatically manages tokens, but if you're implementing your own logic:

```python
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.access_token = None
        self.expires_at = None
    
    def is_token_valid(self):
        if not self.access_token or not self.expires_at:
            return False
        # Add 5-minute buffer
        return datetime.now() < (self.expires_at - timedelta(minutes=5))
    
    def get_token(self):
        if not self.is_token_valid():
            # Request new token
            self.access_token = self.request_new_token()
            self.expires_at = datetime.now() + timedelta(days=30)
        return self.access_token
```

## Common Use Cases

### 1. Bulk Data Export

```python
client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

# Get all workspaces
all_workspaces = []
row_number = 0
limit = 100

while True:
    response = client.post('/2/account/projects', json={
        'limit': limit,
        'row_number': row_number,
        'filter': {'archive_status': [0]}
    })
    workspaces = response.json()
    
    if not workspaces:
        break
    
    all_workspaces.extend(workspaces)
    row_number += limit

print(f'Total workspaces: {len(all_workspaces)}')
```

### 2. Automated Reporting

```python
client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

# Get all boards across workspaces
response = client.post('/2/account/projects', json={'limit': 1000})
workspaces = response.json()

for workspace in workspaces:
    boards_response = client.get(f'/1/projects/{workspace["id"]}/boards')
    boards = boards_response.json()
    print(f'{workspace["name"]}: {len(boards)} boards')
```

### 3. Data Synchronization

```python
client = OAuth2ClientCredentials(CLIENT_ID, CLIENT_SECRET)

# Sync cards from a board
response = client.get('/1/boards/12345/columns')
columns = response.json()

for column in columns:
    cards_response = client.get(f'/1/columns/{column["id"]}/cards')
    cards = cards_response.json()
    # Process cards...
```

## Error Handling

### Authentication Errors

```python
try:
    response = requests.post(
        'https://api.projectplace.com/oauth2/access_token',
        data={'grant_type': 'client_credentials'},
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print('Invalid credentials')
    elif e.response.status_code == 403:
        print('Robot account not authorized')
```

### API Errors

```python
try:
    response = client.get('/1/workspaces/999999')
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print('Resource not found or access denied')
    elif e.response.status_code == 429:
        print('Rate limit exceeded')
```

## Security Best Practices

1. **Never expose credentials**
   - Don't commit `CLIENT_ID` and `CLIENT_SECRET` to version control
   - Use environment variables or secure vaults (e.g., AWS Secrets Manager)

2. **Rotate credentials regularly**
   - Generate new credentials periodically
   - Revoke old credentials after rotation

3. **Limit robot permissions**
   - Only grant necessary permissions to robot accounts
   - Use different robots for different integration purposes

4. **Monitor usage**
   - Log all API calls for audit purposes
   - Monitor for unusual activity patterns

5. **Use HTTPS**
   - Always use HTTPS endpoints
   - Never send credentials over HTTP

## Environment Variables (Recommended)

Instead of hardcoding credentials, use environment variables:

```python
import os

CLIENT_ID = os.environ.get('PROJECTPLACE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PROJECTPLACE_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError('Missing credentials in environment variables')
```

Set them in your environment:

```bash
export PROJECTPLACE_CLIENT_ID='your_client_id'
export PROJECTPLACE_CLIENT_SECRET='your_client_secret'
python oauth2_client_credentials.py
```

## Troubleshooting

### "Invalid client" error

**Cause**: Incorrect `CLIENT_ID` or `CLIENT_SECRET`

**Solution**: 
- Verify credentials from your admin
- Ensure no extra spaces or characters
- Check if the robot account is still active

### "Insufficient permissions" error

**Cause**: Robot account lacks necessary permissions

**Solution**:
- Contact your organization administrator
- Verify the robot has access to the resources you're trying to access
- Check if the workspace/board permissions are correctly configured

### Token expires immediately

**Cause**: System clock is incorrect

**Solution**:
- Ensure your system clock is synchronized
- Token expiration is based on timestamps

## API Documentation

For complete API documentation:
- [OAuth2 Documentation](https://api.projectplace.com/apidocs#articles/pageOAuth2.html)
- [Enterprise Integrations Guide](https://api.projectplace.com/apidocs#articles/pageEnterpriseIntegrations.html)
- [API Reference](https://api.projectplace.com/apidocs)
- [PUC API Documentation](https://github.com/Projectplace/api-code-examples) - For Universal Connector compatible endpoints

## Related Examples

- **OAuth2 Authorization Code Flow** - For user authentication
- **OAuth1 Flow** - Legacy authentication method
- **py-enforce-column-name** - Example using client credentials
- **py-consume-odata** - OData access with client credentials

## Support

For more information:
- [Success Center](https://success.planview.com/Planview_ProjectPlace)
- [API Code Examples Repository](https://github.com/Projectplace/api-code-examples)
- Contact your Planview administrator for robot account setup

