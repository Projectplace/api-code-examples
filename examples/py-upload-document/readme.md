**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Upload a document to the document archive of a workspace

This script demonstrates basic upload functionality towards ProjectPlace. You can choose to upload to the
root of a specific workspace or to a specific folder (if you know the ID of the folder).

1. If you upload the same file several times to the root of a document archive - you will create duplicates 
   because the root document archive does not support versions of documents.
2. If you upload the same file several times to a folder - you will likely append a new version of to the
   already existing document. Folders by default have versioning activated.

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
$ python3 upload-document.py PATH_TO_FILE
```

1. First the script will fetch a list of workspaces which your token allows you to
2. You are then prompted to pick one of them
3. The file designated by PATH_TO_FILE will then be uploaded to the root level of that document archive

You can also upload directly to a specific folder (if you know the ID of the folder), like this:

```
$ python upload_document.py PATH_TO_FILE -f ID_OF_FOLDER
```
