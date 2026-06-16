import json
import os.path
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
    Asks the user to pick a workspace - and returns the ID of the selected workspace's main document
     container - if it is valid
    """
    available_workspaces = requests.get(f'{API_ENDPOINT}/1/user/me/projects?include_tools=true', headers=_get_auth_header()).json()
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
        headers=_get_auth_header()
    )

    return r.json()['id'], r.json()['ver_nr']


def _verify_container(container_id):
    r = requests.get(f'{API_ENDPOINT}/2/documents/{container_id}', headers=_get_auth_header())
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
    _ensure_access_token()
    if not os.path.isfile(file_path):
        print(file_path, 'doesn\'t seem to be a valid file')
        exit(1)

    document_container_id = _verify_container(
        folder_id if folder_id else _choose_workspace()
    )

    document_id, version_number = _do_the_upload(file_path, document_container_id)

    if not version_number:
        print('Document isn\'t in a versioned container - so a new document has been created:', f'https://www.projectplace.com/pp/pp.cgi/r{document_id}')
    else:
        print('New version', version_number, 'of document has been uploaded:', f'https://www.projectplace.com/pp/pp.cgi/r{document_id}')


if __name__ == '__main__':
    argh.dispatch_command(upload_document)
