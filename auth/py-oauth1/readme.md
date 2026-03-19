**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# OAuth1 Robot Account Example

Demonstrates how to use OAuth1 authentication with a robot account to make API calls.

## Prerequisites

```bash
pip install -r requirements.txt
```

## Configuration

Edit the script and replace these values with your robot account credentials:

```python
APPLICATION_KEY = 'your_application_key_here'
APPLICATION_SECRET = 'your_application_secret_here'
ACCESS_TOKEN_KEY = 'your_access_token_key_here'
ACCESS_TOKEN_SECRET = 'your_access_token_secret_here'
SUBDOMAIN = 'your_subdomain_here'
```

## Usage

View account info:
```bash
python oauth1_flow.py account-info
```

Create a project (and immediately delete it):
```bash
python oauth1_flow.py create-project "My Project Name"
```

## Documentation

- [API Reference](https://service.projectplace.com/apidocs/)
- [OAuth1 Guide](https://service.projectplace.com/apidocs/#articles/pageOAuth1.html)
