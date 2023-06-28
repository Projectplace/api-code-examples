import csv
import json
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
    response = requests.get(f'{API_ENDPOINT}/1/account/people', auth=oauth1)

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
            auth=oauth1
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
