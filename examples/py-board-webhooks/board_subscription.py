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


def _board_is_accessible(board_id):
    r = requests.get(
        f'{API_ENDPOINT}/1/boards/{board_id}', headers=_get_auth_header()
    )

    if r.status_code == 200:
        return r.json()['project_id']

    return None


def _subscribe_to_board(board_id, project_id, webhook_url):
    existing_webhooks = requests.get(
        f'{API_ENDPOINT}/1/webhooks/list',
        headers=_get_auth_header()
    ).json()

    for webhook in existing_webhooks:
        if webhook['artifact_type'] == 'board' and webhook['artifact_id'] == board_id and webhook['event_type'] == ['card_status_change']:
            if webhook_url != webhook['webhook']:
                # Webhook URL is different in existing subscription - lets update it
                requests.put(
                    f'{API_ENDPOINT}/1/webhooks/{webhook["id"]}/update',
                    json={
                        'event_type': ['card_status_change'],
                        'webhook': webhook_url
                    },
                    headers=_get_auth_header()
                )
            return webhook

    return requests.post(
        f'{API_ENDPOINT}/1/webhooks',
        json={
            'artifact_type': 'board',
            'artifact_id': board_id,
            'event_type': ['card_status_change'],
            'project_id': project_id,
            'webhook': webhook_url
        },
        headers=_get_auth_header()
    ).json()


def _unsubscribe_to_board(board_id):
    subscription_to_delete = None
    if active_board_subscriptions := _report_subscription_status(board_id):
        for sub in active_board_subscriptions:
            if sub['artifact_type'] == 'board' and sub['artifact_id'] == board_id and sub['event_type'] == ['card_status_change']:
                subscription_to_delete = sub
    if subscription_to_delete:
        requests.delete(
            f'{API_ENDPOINT}/1/webhooks/{subscription_to_delete["id"]}',
            headers=_get_auth_header()
        )


def _report_subscription_status(board_id):
    r = requests.get(
        f'{API_ENDPOINT}/1/webhooks/list',
        headers=_get_auth_header()
    )

    if r.status_code != 200:
        print(f'Failed to list subscriptions {r.content}')

    board_webhooks = []

    for webhook in r.json():
        if webhook['artifact_type'] == 'board' and webhook['artifact_id'] == board_id:
            board_webhooks.append(webhook)

    return board_webhooks


@argh.arg('board-id', help='The ID of a ProjectPlace board to which you have access', type=int)
@argh.arg('-w', '--webhook_url', default='', help='This should be the webhook which should get'
                                                  'invoked when the subscribed event happens')
@argh.arg('-u', '--unsubscribe', default=False, help='Delete the subscription if it exists')
def board_subscription(board_id, *, webhook_url='', unsubscribe=False):
    _ensure_access_token()
    project_id = _board_is_accessible(board_id)
    if not project_id:
        print('Board does not exist or is not accessible with the current credentials')
        exit(1)

    if webhook_url:
        _subscribe_to_board(board_id, project_id, webhook_url)
    elif unsubscribe:
        _unsubscribe_to_board(board_id)

    if active_board_subscriptions := _report_subscription_status(board_id):
        print(f'You have the following subscriptions for board {board_id}')
        print(json.dumps(active_board_subscriptions, indent=2, sort_keys=True))
    else:
        print(f'You have NO subscription for board {board_id}')


if __name__ == '__main__':
    argh.dispatch_command(board_subscription)
