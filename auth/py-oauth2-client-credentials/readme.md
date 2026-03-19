**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.
# OAuth2 Client Credentials Flow Example
Demonstrates how to use OAuth2 Client Credentials flow with a robot/service account.
## Prerequisites
```bash
pip install -r requirements.txt
```
## Configuration
Edit the script and replace these values with your robot account credentials:
```python
CLIENT_ID = 'your_robot_client_id_here'
CLIENT_SECRET = 'your_robot_client_secret_here'
SUBDOMAIN = 'your_subdomain_here'
```
## Usage
```bash
python oauth2_client_credentials.py
```
The script will:
1. Request an access token using client credentials
2. Fetch the first 5 active workspaces from your account
## Documentation
- [API Reference](https://service.projectplace.com/apidocs/)
- [OAuth2 Guide](https://service.projectplace.com/apidocs/oauth2.html)
- [How to Generate a Robot Token](https://success.planview.com/Planview_ProjectPlace/Account_administration/017_Manage_Robots_in_the_Account)
