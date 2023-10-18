import collections
import datetime
import requests
import requests_oauthlib
import argh

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


def get_inactive_users(days):
    """
    We check for users who last logged in earler than `days` ago.

    We also just ask for the first 40 results. This value can be modified by you, or you can make your own
    recursive implementation.

    Note: The query we pose to the API is actually to return people who logged in later than five years ago,
    but before `days` ago. The `last_logged_in` parameter only supports a date range
    """

    from_dt = (datetime.datetime.utcnow() - datetime.timedelta(days=1825)).strftime('%Y-%m-%d')
    to_dt = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')

    inactive_users = requests.post(
        f'{API_ENDPOINT}/1/account/people',
        json={
            'sort_by': '+last_login',
            'filter': {
                'last_logged_in': {'from': from_dt, 'to': to_dt},
                'account_roles': ['account_co_owner', 'account_administrator', 'account_member',
                                  'account_pending_member', 'external_member', 'unregistered']
            },
            'limit': 40,
            'row_number': 0
        },
        auth=oauth1).json()

    return inactive_users


def print_inactive_users(inactive_users, days):
    if inactive_users:
        print(f'The following users last logged in longer than {days} ago')
    now_utc = datetime.datetime.utcnow().date()
    for _i, user in enumerate(inactive_users):
        last_log_in = datetime.datetime.utcfromtimestamp(user['last_login'] / 1000).date()
        print(_i + 1, user['name'], f'({(now_utc - last_log_in).days} days ago)')


def verify_replace_with(replace_with_id, inactive_users):
    """
    We have to verify that the supplied user id of the person who should take over vacated head admin roles is valid.

    The user has to be an account member - and it mustn't be a user who themself will be removed as a result
    of removing inactive users.
    """
    if replace_with_id is None:
        print('You have to specify the ID of a person to whom responsibilities should transfer, use the --replace-with'
              ' argument.')
        return False

    all_account_members = requests.get(
        f'{API_ENDPOINT}/1/account/people', auth=oauth1
    ).json()

    all_account_member_ids = [int(u['id']) for u in all_account_members if u['account_role'] in (
        'account_role_owner', 'account_role_member', 'account_role_admin', 'account_role_co_owner'
    )]

    users_to_remove = [int(u['userid']) for u in inactive_users]

    # The user is an account member
    if replace_with_id not in all_account_member_ids:
        print(f'The intended user {replace_with_id} is not valid to take over responsibilities')
        return False

    # The user is not slated for removal
    if replace_with_id in users_to_remove:
        print(
            f'The intended user {replace_with_id} is itself going to be removed and can therefore not be designated as a replacement!')
        return False

    return [u for u in all_account_members if int(u['id']) == replace_with_id].pop()


def organise_owner_transfers(inactive_users):
    """
    Here we go through each user slated for deletion/removal and check what they are head admins of (if anything).

    We return a dictionary mapping user_ids to owned artifacts, and the name and external status of the user.

    The external status is important later - because we cannot delete external members, only remove them from
    workspaces in the account. External members will never be head administrators of anything in the account.

    Only account members can be head administrators of anything - so only they will actually have any values
    populated for workspaces, portfolios, teams and templates.

        {
            "USER_ID": {
                "name": NAME_OF_USER,
                "is_external: True or False,
                "workspaces": [WORKSPACE_ID, ...],
                "portfolios": [PORTFOLIO_ID, ...],
                "teams": [TEAM_ID, ...],
                "templates": [WORKSPACE_TEMPLATE_ID, ...]
            },
            "USER_ID_2": {
                "name": NAME_OF_USER_2,
                "is_external: True or False,
                "workspaces": [WORKSPACE_ID_2, ...],
                "portfolios": [PORTFOLIO_ID_2, ...],
                "teams": [TEAM_ID_2, ...],
                "templates": [WORKSPACE_TEMPLATE_ID_2, ...]
            },
        }
    """
    users_to_owned_artifacts = collections.defaultdict(dict)

    for _i, user_to_remove in enumerate(inactive_users):
        owner_record = users_to_owned_artifacts[user_to_remove['userid']]
        owner_record['name'] = user_to_remove['name']
        owner_record['is_external'] = user_to_remove['account_role'] == 'account_role_external'
        owned_artifacts = requests.get(
            f'{API_ENDPOINT}/1/account/people/{user_to_remove["userid"]}/owned-artifacts',
            auth=oauth1
        ).json()

        # 1. Workspaces
        if workspace_ownerships := owned_artifacts[user_to_remove['userid']]['projects_data'].get('projects_owner', []):
            users_to_owned_artifacts[user_to_remove['userid']]['workspaces'] = workspace_ownerships

        # 2. Portfolios
        if portfolio_ownerships := owned_artifacts[user_to_remove['userid']].get('portfolios_owner', []):
            users_to_owned_artifacts[user_to_remove['userid']]['portfolios'] = portfolio_ownerships

        # 3. Customer Teams
        if team_ownerships := owned_artifacts[user_to_remove['userid']].get('teams_owner', []):
            users_to_owned_artifacts[user_to_remove['userid']]['teams'] = team_ownerships

        # 4. Workspace Templates
        if template_ownerships := owned_artifacts[user_to_remove['userid']].get('templates_owner', []):
            users_to_owned_artifacts[user_to_remove['userid']]['templates'] = template_ownerships

    return users_to_owned_artifacts


def _remove_account_user(user_id):
    response = requests.post(
        f'{API_ENDPOINT}/1/account/people/{user_id}',
        json={
            'action': 'remove_account_user',
            'params': [
                {
                    user_id: {"workspaces": {}, "templates": {}, "portfolios": {}, "teams": {}}
                }
            ]
        },
        auth=oauth1
    )
    response.raise_for_status()
    try:
        assert response.json()['succeeded'] == [str(user_id)]
    except AssertionError:
        print(f'Could not remove {user_id}')


def _delete_account_user(user_id, ownerships=None, replace_with=None):
    ownerships_payload = {
        user_id: {"workspaces": {}, "templates": {}, "portfolios": {}, "teams": {}}
    }
    if ownerships and replace_with:

        ownerships_payload = {
            user_id: {
                'workspaces': {
                    _item['id']: replace_with['id'] for _item in ownerships.get('workspaces', [])
                },
                'portfolios': {
                    _item['id']: replace_with['id'] for _item in ownerships.get('portfolios', [])
                },
                'templates': {
                    _item['id']: replace_with['id'] for _item in ownerships.get('templates', [])
                },
                'teams': {
                    _item['id']: replace_with['id'] for _item in ownerships.get('teams', [])
                }
            }
        }
    response = requests.post(
        f'{API_ENDPOINT}/1/account/people/{user_id}',
        json={
            'action': 'delete_account_user',
            'params': [
                ownerships_payload
            ]
        },
        auth=oauth1
    )

    response.raise_for_status()
    try:
        assert response.json()['succeeded'] == [str(user_id)]
    except AssertionError:
        print(f'Could not delete {user_id}')


def execute_removal(owner_transfers, replace_with):
    """
    After having investigated which that need to have their head admin roles replaced we go ahead and
    print each user. Showing what the result of the deletion/removal will be and we ask the user to
    confirm each deletion/removal.
     """

    _i = 1
    for user_id, ownerships in owner_transfers.items():
        owner = False
        if any(i in ownerships.keys() for
               i in ('workspaces', 'portfolios', 'teams', 'templates')):
            owner = True
            print(f'{_i} {ownerships["name"]} is head administrator of the following things')

            for _j, workspace in enumerate(ownerships.get('workspaces', [])):
                print(f'  Workspace {_j + 1}: "{workspace["name"]}"')

            for _j, template in enumerate(ownerships.get('templates', [])):
                print(f'  Workspace template {_j + 1}: "{template["name"]}"')

            for _j, portfolio in enumerate(ownerships.get('portfolios', [])):
                print(f'  Portfolio {_j + 1}: "{portfolio["name"]}"')

            for _j, team in enumerate(ownerships.get('teams', [])):
                print(f'  Team {_j + 1}: "{team["name"]}"')

        if owner:
            confirm = input(f'{_i}. Do you want to delete {ownerships["name"]}? (Head admin roles '
                            f'will be transferred to {replace_with["name"]}) (y/N): ')
        else:
            confirm = input(
                f'{_i}. Do you want to {"remove" if ownerships["is_external"] else "delete"} {ownerships["name"]} {"(External)" if ownerships["is_external"] else ""}? (y/N): ')

        if confirm and confirm.upper() == 'Y':
            if owner:
                print(f' OK! Deleting {ownerships["name"]} and transferring head admin roles.')
                _delete_account_user(user_id, ownerships, replace_with)
            elif ownerships['is_external']:
                print(f' OK! Removing {ownerships["name"]} from the account')
                _remove_account_user(user_id)
            else:
                print(f' OK! Deleting {ownerships["name"]}')
                _delete_account_user(user_id)
        else:
            print(f' OK! {ownerships["name"]} will not be {"removed" if ownerships["is_external"] else "deleted"}.')

        _i += 1


@argh.arg('days', type=int, help='The number of days back it time to check for last logins of users, e.g 30 (days)')
@argh.arg('replace-with', type=int,
          help='Specify the ID of a person who should take over the head admin roles of whoever gets deleted')
def main(days: int, replace_with: int):
    inactive_users = get_inactive_users(days)

    if not inactive_users:
        print(f'Couldn\'t find any inactive users (where last login is older than {days} days ago).')

    if replace_with_user := verify_replace_with(replace_with, inactive_users):
        owner_transfers = organise_owner_transfers(inactive_users)
        execute_removal(owner_transfers, replace_with_user)
    else:
        exit(1)


if __name__ == '__main__':
    argh.dispatch_command(main)
