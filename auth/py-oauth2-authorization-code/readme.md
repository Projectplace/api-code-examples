**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.
# OAuth2 Authorization Code Flow Example
Demonstrates how to use OAuth2 Authorization Code flow for user authentication.
## Prerequisites
```bash
pip install -r requirements.txt
```
## Configuration
Edit the script and replace these values with your application credentials:
```python
CLIENT_ID = 'your_client_id_here'
CLIENT_SECRET = 'your_client_secret_here'
SUBDOMAIN = 'your_subdomain_here'
```
## Usage
```bash
python oauth2_authorization_code.py
```
The script will:
1. Open your browser for authorization
2. Prompt you to enter the authorization code
3. Exchange the code for access tokens
4. Fetch your user profile to verify it works
## Documentation
- [API Reference](https://service.projectplace.com/apidocs/)
- [OAuth2 Guide](https://service.projectplace.com/apidocs/#articles/pageOAuth2.html)
