import csv
import json
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


def get_email_changes(csv_file):

    mapping = {}
    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, ['existing', 'new'])

        for row in reader:
            mapping[row['existing'].lower()] = row['new'].lower()

    return mapping


def get_valid_email_changes(existing_emails):
    """
    Compare the list of existing emails to emails of actual account members. Return a mapping where
    only account members are represented.
    """
    response = requests.get(f'{API_ENDPOINT}/1/account/people', headers=_get_auth_header())

    assert response.status_code == 200

    valid_user_changes = {}
    for user in response.json():
        if user['email'].lower() in existing_emails.keys() and user['account_role'] in (
            'account_role_owner', 'account_role_co_owner', 'account_role_admin', 'account_role_member'
        ):
            valid_user_changes[user['email'].lower()] = {
                'id': int(user['id']),
                'email': existing_emails[user['email'].lower()]
            }

    return valid_user_changes


def change_emails(emails_to_change):
    failures = []
    successes = []
    for existing, new in emails_to_change.items():
        print('Updating email of', existing)
        r = requests.post(
            f'{API_ENDPOINT}/1/account/people/{new["id"]}',
            json={'action': 'add_secondary_email', 'params': [new['email']]},
            headers=_get_auth_header()
        )
        if r.status_code != 200:
            failures.append(existing)
        else:
            print(json.dumps(r.json(), indent=2, sort_keys=True))
            if str(new['id']) in r.json()['succeeded']:
                successes.append(existing)
            elif str(new['id']) in r.json()['failed']:
                failures.append(existing)

    return successes, failures


def bulk_update_emails(csv_file):
    _ensure_access_token()
    email_changes = get_email_changes(csv_file)

    all_mapped_account_members = get_valid_email_changes(email_changes)

    print('The following email changes will be attempted')
    for existing, new in all_mapped_account_members.items():
        print(existing, ' => ', new)

    confirmation = input('Do you want to proceed? (Y/n) ')

    if confirmation and confirmation.upper() != 'Y':
        print('Abandoning')
        exit()

    successes, failures = change_emails(all_mapped_account_members)

    print('The following emails were successfully updated', successes)


if __name__ == '__main__':
    argh.dispatch_command(bulk_update_emails)
