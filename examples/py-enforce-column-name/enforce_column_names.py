import textwrap
import requests
import requests.auth
import argh

CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'
access_token = None


def _hide_cursor():
    print('\033[?25l', end="")


def _show_cursor():
    print('\033[?25h', end="")


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
    return {
        'Authorization': f'Bearer {access_token}'
    }


def _get_workspaces(limit=100, row_number=0):
    """
    Paginate through all workspaces in the account. Returns a list populated with workspace objects.

    Ignores archived workspaces
    """
    request_body = {
        'sort_by': '+creation_date',
        'filter': {
            'archive_status': [0]
        },
        'limit': limit
    }
    if row_number:
        request_body.update({'row_number': row_number})

    r = requests.post(f'{API_ENDPOINT}/2/account/projects', json=request_body, headers=_get_auth_header())

    response_json = r.json()

    workspaces = r.json()
    if len(response_json) == limit:
        workspaces += _get_workspaces(limit=limit, row_number=row_number + limit)

    return workspaces


def _get_boards_for_workspaces(workspaces):
    boards = []
    for workspace in workspaces:
        response = requests.get(f'{API_ENDPOINT}/1/projects/{workspace["id"]}/boards', headers=_get_auth_header())
        if response.ok:
            boards += response.json()

    return boards


def _filter_out_relevant_boards(boards, column_order, new_column_name,  old_column_name):
    relevant_boards = []

    for board in boards:
        # Ignore if the column order does not exist
        if column_order > len(board['progresses']) - 1:
            continue

        # Ignore if old column name has been specified and does not match
        if old_column_name is not None and board['progresses'][column_order]['name'] != old_column_name:
            continue

        # Ignore if the current name is already the new name
        if new_column_name == board['progresses'][column_order]['name']:
            continue

        relevant_boards.append(board)

    return relevant_boards


def _confirm_pending_changes(relevant_boards, column_order, new_column_name, old_column_name):
    if old_column_name:
        print(
            textwrap.dedent(
                f'''
                You are about to do the following:
                
                    1. Column in position {column_order} will be renamed to "{new_column_name}" 
                    2. This will occur on {len(relevant_boards)} board(s) - where the name of the column
                       in that position right now is "{old_column_name}"
                '''
            )
        )
    else:
        print(
            textwrap.dedent(
                f'''
                You are about to do the following:
                
                    1. Column in position {column_order} will be renamed to "{new_column_name}" 
                    2. This will occur on {len(relevant_boards)} board(s).
                '''
            )
        )
    confirm = input('Type "Yes" and press [ENTER] to confirm: ')
    if confirm.upper() == 'YES':
        return True

    return False


def _execute_changes(boards, column_order, new_column_name):
    print('Starting update')
    _hide_cursor()
    for _i, board in enumerate(boards):
        response = requests.post(
            f'{API_ENDPOINT}/1/boards/{board["id"]}/statuses/{board["progresses"][column_order]["id"]}/properties',
            json={
                'name': new_column_name
            },
            headers=_get_auth_header()
        )
        response.raise_for_status()
        print(f'{_i + 1}/{len(boards)} completed', end='\r', flush=True)
    _show_cursor()
    print('\nDone!')


def enforce_column_names(column_order: int, new_column_name: str, *, old_column_name: str = None):
    _ensure_access_token()
    workspaces = _get_workspaces()
    boards = _get_boards_for_workspaces(workspaces)
    relevant_boards = _filter_out_relevant_boards(boards, column_order, new_column_name, old_column_name)
    if not relevant_boards:
        print('No matching boards found')
        exit(0)
    if _confirm_pending_changes(relevant_boards, column_order, new_column_name, old_column_name):
        _execute_changes(relevant_boards, column_order, new_column_name)
    else:
        print('Operation aborted - no changes have been made.')


if __name__ == '__main__':
    argh.dispatch_command(enforce_column_names)
