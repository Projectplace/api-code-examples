**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# List contents of document archive of a Workspace

This script asks you for the ID of a workspace - and then saves JSON-formatted list of the contents
of the document archive in that workspace.

The script requires an OAuth1 token to operate and it assumes that you have already obtained one.

### 1. Install requirements

See the `requirements.txt` file for needed third-party libraries.

You can install them by running `pip install -r requirements.txt`

### 2. Modify the script with your authorization attributes

The following section needs to be replaced with application key/secret and your OAuth1 token key/secret.

```
APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'
ACCESS_TOKEN_KEY = 'REDACTED'
ACCESS_TOKEN_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'
```

### 3. Run the script

```
$ python3 list-document-archive.py
```

1. First the script will fetch a list of workspaces which your token allows you to access - it will
   then print these workspaces and their IDs.
2. Then the script will ask you which workspace you wish list the document archive for. Enter the ID of the
   workspace you are interested in.
3. Once the contents have been fetched - they will be saved in a json file in the working directory.
