# Authentication Mechanisms for Planview ProjectPlace API

This directory contains examples for all supported authentication methods for the Planview ProjectPlace API.

## Available Authentication Methods

### 1. OAuth2 Authorization Code Flow ⭐ Recommended for User Access
**Directory**: `py-oauth2-authorization-code/`

Use this when you need to access resources **on behalf of a user**.

**Best for:**
- Web applications
- Mobile apps
- Desktop applications
- Any integration where users authorize your app to access their data

**Key Features:**
- User authorizes your application
- Access tokens valid for 30 days
- Refresh tokens valid for 120 days
- Can maintain indefinite access with refresh tokens

[View Example →](./py-oauth2-authorization-code)

---

### 2. OAuth2 Client Credentials Flow ⭐ Recommended for Service Accounts
**Directory**: `py-oauth2-client-credentials/`

Use this for **robot/service account** authentication without user interaction.

**Best for:**
- Server-to-server integrations
- Automated scripts and workflows
- Bulk data operations
- Account-wide integrations
- Background jobs and scheduled tasks

**Key Features:**
- No user interaction required
- Account-wide access
- Simple authentication flow
- Access tokens valid for 30 days

[View Example →](./py-oauth2-client-credentials)

---

### 3. OAuth1 (Legacy)
**Directory**: `py-oauth1/`

**⚠️ Legacy Method** - Only use for maintaining existing integrations.

For new projects, use OAuth2 instead.

[View Example →](./py-oauth1)

---

## Quick Comparison

| Method | Use Case | User Interaction | Token Lifetime | Refresh Token |
|--------|----------|------------------|----------------|---------------|
| **OAuth2 Authorization Code** | User access | Required | 30 days | Yes (120 days) |
| **OAuth2 Client Credentials** | Service accounts | Not required | 30 days | No (just request new) |
| **OAuth1** | Legacy | Required | Permanent | No |

---

## Choosing the Right Authentication Method

### Use OAuth2 Authorization Code Flow when:
✅ Your app needs to act on behalf of users  
✅ You need user-specific permissions  
✅ Building a web/mobile/desktop app  
✅ Users should control access to their data  

### Use OAuth2 Client Credentials Flow when:
✅ Building server-to-server integration  
✅ Need account-wide access (not user-specific)  
✅ Automating bulk operations  
✅ Running scheduled jobs  
✅ No user interaction is possible/desired  

### Use OAuth1 only when:
⚠️ Maintaining existing OAuth1 integration  
⚠️ Required by legacy systems  

---

## Getting Started

### For User Authentication (OAuth2 Authorization Code)

1. **Register your application** in ProjectPlace
   - Go to Settings → Developer → Applications
   - Create new application
   - Note Client ID and Client Secret
   - Set Redirect URI

2. **Try the example**
   ```bash
   cd py-oauth2-authorization-code
   pip install -r requirements.txt
   # Edit oauth2_authorization_code.py with your credentials
   python oauth2_authorization_code.py
   ```

3. **Read the documentation**
   - [OAuth2 Authorization Code README](./py-oauth2-authorization-code/readme.md)
   - [API Documentation](https://api.projectplace.com/apidocs#articles/pageOAuth2.html)

### For Service Account Authentication (OAuth2 Client Credentials)

1. **Get robot credentials** from your administrator
   - Admin goes to Account Administration → Integration settings
   - Create robot user
   - Generate OAuth2 credentials
   - Receive Client ID and Client Secret

2. **Try the example**
   ```bash
   cd py-oauth2-client-credentials
   pip install -r requirements.txt
   # Edit oauth2_client_credentials.py with your credentials
   python oauth2_client_credentials.py
   ```

3. **Read the documentation**
   - [OAuth2 Client Credentials README](./py-oauth2-client-credentials/readme.md)
   - [Setup Guide](https://success.planview.com/Planview_ProjectPlace/Integrations/Integrate_with_Planview_Hub%2F%2FViz_(Beta))

---

## API Endpoints

All authentication methods work with the same API endpoints:

**Base URL**: `https://api.projectplace.com`

**Common Endpoints:**
- `/1/user/me` - Get current user info
- `/1/user/me/projects` - Get workspaces
- `/1/projects/{id}/boards` - Get boards
- `/1/boards/{id}/columns` - Get board columns
- `/1/columns/{id}/cards` - Get cards
- `/2/account/projects` - Get all account workspaces (requires appropriate permissions)

**Authorization Header:**
```
Authorization: Bearer {access_token}
```

---

## Security Best Practices

### Never Commit Credentials
❌ Don't commit `CLIENT_ID`, `CLIENT_SECRET`, or tokens to version control

✅ Use environment variables:
```python
import os
CLIENT_ID = os.environ.get('PROJECTPLACE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('PROJECTPLACE_CLIENT_SECRET')
```

### Always Use HTTPS
❌ Never use HTTP endpoints  
✅ Always use HTTPS: `https://api.projectplace.com`

### Store Tokens Securely
❌ Don't store tokens in plain text  
✅ Use encryption, secure vaults (AWS Secrets Manager, Azure Key Vault, etc.)

### Rotate Credentials Regularly
✅ Generate new credentials periodically  
✅ Revoke old credentials after rotation  

### Monitor API Usage
✅ Log all API calls for audit  
✅ Set up alerts for unusual activity  
✅ Implement rate limiting in your application  

---

## Additional Examples Using These Auth Methods

Once you understand authentication, check out these examples that use the auth methods:

- **py-download-document** - Download files using OAuth1
- **py-upload-document** - Upload files
- **py-enforce-column-name** - Bulk board updates using Client Credentials
- **py-consume-odata** - Access OData feeds using Client Credentials
- **py-board-webhooks** - Set up webhooks
- **py-bulk-update-emails** - Bulk user operations

---

## Troubleshooting

### Common Issues

**"Invalid client" error**
- Check your CLIENT_ID and CLIENT_SECRET
- Ensure no extra spaces or characters
- Verify credentials are for the correct environment

**"Redirect URI mismatch" (OAuth2 Authorization Code)**
- Redirect URI in code must exactly match app settings
- Include protocol (http:// or https://)
- Match port number exactly

**"Insufficient permissions"**
- For user auth: User must have appropriate access
- For robot auth: Robot account must be granted access by admin
- Check workspace/board-level permissions

**Tokens expire immediately**
- Check your system clock is synchronized
- Token expiration is based on timestamps

---

## API Documentation & Resources

### Official Documentation
- [API Documentation](https://api.projectplace.com/apidocs)
- [OAuth2 Guide](https://api.projectplace.com/apidocs#articles/pageOAuth2.html)
- [Success Center](https://success.planview.com/Planview_ProjectPlace)

### Code Examples Repository
- [GitHub: api-code-examples](https://github.com/Projectplace/api-code-examples)

### Support
- Contact your Planview administrator for robot account setup
- [Planview Support](https://success.planview.com)

---

## Contributing

Found an issue or have an improvement? Contributions welcome!

---

**Last Updated**: March 2026

**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit, Planview does not accept any liability or responsibility for you choosing to do so.

