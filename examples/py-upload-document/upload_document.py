import json
import os.path
import argh
import requests
import requests_oauthlib



APPLICATION_KEY = '65a7b8a09cad1c8a514968d3ae0dcea4'
APPLICATION_SECRET = 'baf74123d0897cc61652d7b458638ad12791160f'
ACCESS_TOKEN_KEY = '04b12136a5093ac378304449171d83a4'
ACCESS_TOKEN_SECRET = '448ed69b90659cd97c3a5b6e99a6651682b0ced7'
API_ENDPOINT = 'https://api-compose.rnd.projectplace.com'


oauth1 = requests_oauthlib.OAuth1(
    client_key=APPLICATION_KEY,
    client_secret=APPLICATION_SECRET,
    resource_owner_key=ACCESS_TOKEN_KEY,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)


def _choose_workspace():
    """
    Asks the user to pick a workspace - and returns the ID of the selected workspace's main document
     container - if it is valid
    """
    available_workspaces = requests.get(f'{API_ENDPOINT}/1/user/me/projects?include_tools=true', auth=oauth1).json()
    print('You have access to the following workspaces:')
    for workspace in available_workspaces:
        print(f'{workspace["name"]} ID: {workspace["id"]}')

    workspace_id = input('\nEnter workspace ID here: ')

    for ws in available_workspaces:
        if str(ws['id']) == workspace_id:
            return ws['tools']['documents']['container_id']

    print('\nError: That isn\'t a valid workspace ID')
    exit(1)


def _do_the_upload(file_path, document_container_id):
    file_name = os.path.split(file_path)[-1]

    r = requests.post(
        f'{API_ENDPOINT}/2/documents/{document_container_id}/upload',
        files={file_name: open(file_path, 'rb')},
        auth=oauth1
    )

    return r.json()['id'], r.json()['ver_nr']


def _verify_container(container_id):
    r = requests.get(f'{API_ENDPOINT}/2/documents/{container_id}', auth=oauth1)
    response_json = r.json()

    if 'container_id' not in response_json:
        print('Error:', container_id, 'is not a valid document container')
        exit(1)
    if response_json.get('access') != 'write':
        print('Error: You don\'t have write access to the folder')
        exit(1)

    return container_id


@argh.arg('file_path')
@argh.arg('-f', '--folder-id', type=int, default=None)
def upload_document(file_path, *, folder_id=None):
    if not os.path.isfile(file_path):
        print(file_path, 'doesn\'t seem to be a valid file')
        exit(1)

    document_container_id = _verify_container(
        folder_id if folder_id else _choose_workspace()
    )

    document_id, version_number = _do_the_upload(file_path, document_container_id)

    if not version_number:
        print('Document isn\'t in a versioned container - so a new document has been created:', f'https://compose.rnd.projectplace.com/pp/pp.cgi/r{document_id}')
    else:
        print('New version', version_number, 'of document has been uploaded:', f'https://compose.rnd.projectplace.com/pp/pp.cgi/r{document_id}')


if __name__ == '__main__':
    argh.dispatch_command(upload_document)
