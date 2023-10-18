import os.path
import urllib.parse
import argh
import requests
import requests_oauthlib


APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'
ACCESS_TOKEN_KEY = 'REDACTED'
ACCESS_TOKEN_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'


oauth1 = requests_oauthlib.OAuth1(
    client_key=APPLICATION_KEY,
    client_secret=APPLICATION_SECRET,
    resource_owner_key=ACCESS_TOKEN_KEY,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)


def _choose_workspace():
    """
    Asks the user to pick a workspace - and returns the ID of the selected workspace if it is valid
    """
    available_workspaces = requests.get(f'{API_ENDPOINT}/1/user/me/projects', auth=oauth1).json()

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
    with requests.get(f'{API_ENDPOINT}/1/documents/{document["id"]}', auth=oauth1, stream=True) as r:
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
    contents = requests.get(f'{API_ENDPOINT}/2/documents/{document_container_id}', auth=oauth1).json()['contents']

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

    if document_id is None:
        # Step 1 - which workspace should we list documents for?
        workspace_id = _choose_workspace()

        # Step 2 - Ask the user to designate which document to download
        _get_document_container_contents(workspace_id)
    else:
        document = requests.get(f'{API_ENDPOINT}/2/documents/{document_id}', auth=oauth1).json()

        _download_document(document)


if __name__ == '__main__':
    argh.dispatch_command(main)
