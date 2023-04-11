import datetime
import json
import os.path
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


def _get_document_container_contents(workspace_id):
    """
    Returns the contents of the root of a workspace document container
    """
    return requests.get(f'{API_ENDPOINT}/2/documents/{workspace_id}', auth=oauth1).json()


def _save_to_file(workspace_id, document_archive_root_contents):
    """
    Saves the contents to a file named WORKSPACE_ID-DATETIME.json
    """
    filename = f'{workspace_id}-{datetime.datetime.now().isoformat(timespec="seconds")}.json'
    with open(filename, 'w') as fp:
        fp.write(json.dumps(document_archive_root_contents, indent=2, sort_keys=True))

    print('The contents have been saved to', os.path.abspath(filename))


def main():
    # Step 1 - which workspace should we list documents for?
    workspace_id = _choose_workspace()

    # Step 2 - get the contents of the document archive of the workspaces
    document_archive_root_contents = _get_document_container_contents(workspace_id)

    _save_to_file(workspace_id, document_archive_root_contents)


if __name__ == '__main__':
    main()
