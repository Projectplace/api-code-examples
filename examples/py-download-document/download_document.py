import os.path
import urllib.parse
import argh
import requests
import requests.auth


CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'

access_token = None


def _ensure_access_token():
    """
    We ask for a new access token on every script run - in normal circumstances you can hold on to an access
    token for longer than that.

    This function uses the client credentials flow which only works for robot accounts since it is intended for
    application-to-application communication. So the client_id and client_secret needs to belong to a robot and the
    resulting access token will also belong to the robot.
    """
    global access_token
    access_token_response = requests.post(
        f'{API_ENDPOINT}/oauth2/access_token',
        data={
            'grant_type': 'client_credentials',
        },
        auth=requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    )
    access_token_response.raise_for_status()
    access_token = access_token_response.json()['access_token']


def _get_auth_header():
    return {'Authorization': f'Bearer {access_token}'}


def _choose_workspace():
    """
    Asks the user to pick a workspace - and returns the ID of the selected workspace if it is valid
    """
    available_workspaces = requests.get(f'{API_ENDPOINT}/1/user/me/projects', headers=_get_auth_header()).json()

    print('\nYou have access to the following workspaces:')

    for workspace in available_workspaces:
        print(f'{workspace["name"]} ID: {workspace["id"]}')

    workspace_id = input('\nEnter workspace ID here: ')

    for ws in available_workspaces:
        if str(ws['id']) == workspace_id:
            return ws['id']

    print('\nError: That isn\'t a valid workspace ID')
    exit(1)


def _download_document(document):
    # While the filename is returned in the dowload response (in the content disposition header) - it is easier
    # so simply use the name as stated in the metadata API response for the document. The "os_file_name" should
    # not contain any forbidden characters - but is urlencoded so we unquote it.
    filename = urllib.parse.unquote(document['os_file_name'])
    print('Downloading...')
    with requests.get(f'{API_ENDPOINT}/1/documents/{document["id"]}', headers=_get_auth_header(), stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as fp:
            for chunk in r.iter_content(chunk_size=8192):
                fp.write(chunk)
    print('Download complete:', os.path.abspath(filename))


def _get_document_container_contents(document_container_id):
    """
    Returns the contents of the root of a workspace document container
    """

    # The actual contents of the document container is found in the "contents" attribute
    contents = requests.get(f'{API_ENDPOINT}/2/documents/{document_container_id}', headers=_get_auth_header()).json()['contents']

    folders = []
    documents = []

    for item in contents:
        if item['type'] == 'Folder':
            folders.append(item)
        if item['type'] == 'Document':
            documents.append(item)

    print('\nFolders:')
    for folder in folders:
        print(folder['file_name'], folder['id'])

    print('\nDocuments')
    for document in documents:
        print(f'{document["file_name"]} ID: {document["id"]}')

    folder_or_document_id = input('Give the ID of a folder or document: ')

    for item in contents:
        if str(item['id']) == folder_or_document_id:
            # If folder - list its contents
            if item['type'] == 'Folder':
                return _get_document_container_contents(item['id'])
            # If document - download
            if item['type'] == 'Document':
                return _download_document(item)

    print('Not a valid document or folder ID - relisting current contents')
    _get_document_container_contents(document_container_id)


@argh.arg('-d', '--document-id', type=int, default=None)
def main(*, document_id=None):
    _ensure_access_token()

    if document_id is None:
        # Step 1 - which workspace should we list documents for?
        workspace_id = _choose_workspace()

        # Step 2 - Ask the user to designate which document to download
        _get_document_container_contents(workspace_id)
    else:
        document = requests.get(f'{API_ENDPOINT}/2/documents/{document_id}', headers=_get_auth_header()).json()

        _download_document(document)


if __name__ == '__main__':
    argh.dispatch_command(main)
