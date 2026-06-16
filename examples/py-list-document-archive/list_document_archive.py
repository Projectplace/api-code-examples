import datetime
import json
import os.path
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


def _get_document_container_contents(workspace_id):
    """
    Returns the contents of the root of a workspace document container
    """
    return requests.get(f'{API_ENDPOINT}/2/documents/{workspace_id}', headers=_get_auth_header()).json()


def _save_to_file(workspace_id, document_archive_root_contents):
    """
    Saves the contents to a file named WORKSPACE_ID-DATETIME.json
    """
    filename = f'{workspace_id}-{datetime.datetime.now().isoformat(timespec="seconds")}.json'
    with open(filename, 'w') as fp:
        fp.write(json.dumps(document_archive_root_contents, indent=2, sort_keys=True))

    print('The contents have been saved to', os.path.abspath(filename))


def main():
    _ensure_access_token()
    # Step 1 - which workspace should we list documents for?
    workspace_id = _choose_workspace()

    # Step 2 - get the contents of the document archive of the workspaces
    document_archive_root_contents = _get_document_container_contents(workspace_id)

    _save_to_file(workspace_id, document_archive_root_contents)


if __name__ == '__main__':
    main()
