**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# OAuth1 Authentication Example

This example demonstrates how to use OAuth1 authentication with the Planview ProjectPlace API.

## Important Note

**OAuth1 is a legacy authentication method.** For new integrations, we strongly recommend using:
- **OAuth2 Authorization Code Flow** - For user authentication
- **OAuth2 Client Credentials Flow** - For robot/service accounts

However, this example is provided for maintaining existing OAuth1 integrations.

## Prerequisites

### Install Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP library
- `requests-oauthlib` - OAuth1 support for requests
- `oauth2` - OAuth1 protocol implementation

### Configuration

Edit the script and replace these values:

```python
APPLICATION_KEY = 'your_application_key_here'
APPLICATION_SECRET = 'your_application_secret_here'
```

## Usage

```bash
python oauth1_flow.py
```

The script will:
1. Request a temporary request token
2. Open your browser for authorization
3. Prompt you to enter the OAuth verifier code
4. Exchange for permanent access tokens
5. Demonstrate API calls

## Making API Calls

Once you have access tokens:

```python
import requests
import requests_oauthlib

oauth1 = requests_oauthlib.OAuth1(
    client_key=APPLICATION_KEY,
    client_secret=APPLICATION_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)

response = requests.get(
    'https://api.projectplace.com/1/user/me',
    auth=oauth1
)

user_data = response.json()
```

## Token Characteristics

- **Request Token**: Temporary token used for authorization (expires quickly)
- **Access Token**: Permanent token for API access (does not expire but can be revoked)
- **No Refresh Token**: OAuth1 tokens don't expire, so no refresh mechanism is needed

## Migration to OAuth2

For new projects, use OAuth2 instead:
- **[OAuth2 Authorization Code Flow](../py-oauth2-authorization-code/)** - For user authentication
- **[OAuth2 Client Credentials Flow](../py-oauth2-client-credentials/)** - For service accounts

## Documentation

For complete API documentation:
- [API Reference](https://api.projectplace.com/apidocs)
- [OAuth2 Guide](https://api.projectplace.com/apidocs#articles/pageOAuth2.html)

## Related Examples

- **py-download-document** - Example using OAuth1 for document operations

