**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Download (and delete) archived workspaces

This script showcases how to download archived workspaces and to delete them (after successful download).

A workspace download is simply a zip file containing most (but not all) of the data in a workspace.

This script helps you understand a few different things.

1. How to trigger the export job and how to wait for it to finish
2. How to download big files in a safe and resource minimising way

The script requires an OAuth1 token to operate and it assumes that you have already obtained one.
The same logic will work with an OAuth2 token.

In a real production setting this type of functionality would be using a "robot account" - i.e a set
of OAuth1 keys/secrets that have super user privileges and therefore has access to all workspaces.

The OAuth token must at the very least belong to an account administrator - since only they have
access to the required artefacts.

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
$ python3 download_workspaces.py
```

This will loop through all workspaces in the account, trigger the export job, and wait for it to complete 
for each of them in succession and then finally download a zip file representing each workspace.

The zip files will by default be downloaded to the working directory - but you can supply a path parameter
as such:

```
$ python3 download_workspaces.py -p /Users/MyUser/WorkspaceDownloads
```

On subsequent runs the script will ignore any workspaces that you have already downloaded.

In order to delete archived workspaces after having downloaded - supply the `-d` argument. As such:

```
$ python3 download_workspaces -p /Users/MyUser/WorkspaceDownloads -d
```

This will delete archived workspaces from ProjectPlace after having downloaded them.  As a safety measure - 
only workspaces for which you have downloaded a zip-file will be deleted from ProjectPlace.
