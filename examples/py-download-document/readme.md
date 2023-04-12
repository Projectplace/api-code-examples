# Download a document from ProjectPlace

This script showcases how to download a document from ProjectPlace.

Documents are found throughout ProjectPlace. In the main document tool of each workspace and
as attachments to different artefacts for example Cards.

This script helps you understand a few different things.

1. How to recursively browse the document structure of a workspace's main document archive.
2. How to download a document.

If you already know the ID of a document you can supply it as an argument to the script. If 
you do not - the script will help you designate a particular document for download.

The script requires an OAuth1 token to operate and it assumes that you have already obtained one.
The same logic will work with an OAuth2 token.

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
$ python3 download-document.py -d DOCUMENT_ID
```

This will immediately download the document (if it is a valid document that you have access to) to the working
directory and exit.

If you omit the `-d DOCUMENT_ID` argument of the script the following happens instead:

1. First the script will fetch a list of workspaces which your token allows you to access - it will
   then print these workspaces and their IDs.
2. Then the script will ask you which workspace you wish list the document archive for. Enter the ID of the
   workspace you are interested in.
3. The script will then ask you to designate a document for download or a folder to look into.
4. If you select a folder ID - the script will show you the contents of that folder - you can continue to do
   this until there aren't any deeper levels. If you end up in a folder that is empty - you will have to manually
   exit the script.
5. Once you designate a document to download, it will be downloaded to the working directory and
   the script exits.
