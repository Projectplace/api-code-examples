**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Board Webhook Example

This showcases how to subscribe to events that happen on a ProjectPlace board via webhooks.

In this example - we limit ourselves to set up a subscription for card column changes on a board.

### 1. Install requirements

See the `requirements.txt` file for needed third-party libraries.

You can install them by running `pip install -r requirements.txt`

### 2. Modify the script with your authorization attributes

The following section needs to be replaced with application key/secret and your OAuth1 token key/secret.

```
APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'
ACCESS_TOKEN_KEY = 'REDACTED'
ACCESS_TOKEN_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'
```

### 3. Subscribing to card column changes

The following will set up a subscription that will send a payload to a designated URL everytime a card
is moved from one column to another on a specific BOARD_ID.

```
$ python3 board_subscription.py BOARD_ID --webhook-url https://URL_TO_YOUR_WEBHOOK_ENDPOINT.com 
```

The following payload will be sent to the `webhook-url`:

```json5
{
  // The ID of the subscription:
  "id": "649c37e5fdfaa1bf202a098e",
  // The artifact type "board":
  "artifact_type": "board",
  // The ID of the Board:
  "artifact_id": 1358069,
  // The event type that caused the payload to sent to the webhook url
  "event_type": "card_status_change",
  // The time at which the event was triggered:
  "ts": 1687960180.368427,
   // A representation of the affected card:
  "contents": {
    "access": "write",
    "all_attachments": [],
    "assignee": null,
    "assignee_id": null,
    "board_column_order": 1,
    "board_id": 1358069,
    "board_name": "Test Board Hooks",
    "checklist": null,
    "column_first_updated": "2023-06-28 13:49:40Z",
    "column_id": 1,
    "column_last_updated": "2023-06-28 13:49:40Z",
    "comment_count": 0,
    "connected_issues": [],
    "connected_risks": [],
    "contributors": [],
    "created_time": "2023-06-28 13:49:31Z",
    "creator": {
      "avatar": "/images/00/16/ed/7317-a98d28e5.jpeg",
      "id": 259895408,
      "name": "NAME OF CARD CREATOR",
      "type": "User"
    },
    "dependencies": {
      "predecessors": 0,
      "predecessors_done": 0,
      "successors": 0,
      "successors_done": 0
    },
    "description": "",
    "direct_url": "https://service.projectplace.com/#direct/card/18776663",
    "display_order": 125000,
    "due_date": null,
    "due_date_offset": null,
    "estimate": null,
    "estimated_time": null,
    "id": 18776663,
    "is_blocked": false,
    "is_blocked_reason": null,
    "is_done": false,
    "is_template": false,
    "label_id": null,
    "local_id": 154,
    "planlet": {
      "id": 978642950,
      "name": "123",
      "wbs_id": "1"
    },
    "planlet_id": 978642950,
    "progress": {
      "id": 1
    },
    "project": {
      "id": 663309443,
      "is_team_member_plus": false,
      "is_team_member_plus_plan": null,
      "name": "TITLE OF WORKSPACE",
      "override_tm_plus_time_reporting": false,
      "type": "classic"
    },
    "reported_time": null,
    "start_date": null,
    "start_date_offset": null,
    "title": "TITLE OF CARD"
   }
}

```

### 4. Unsubscribing
The following will delete the subscription:

```
$ python3 board_subscription.py BOARD_ID --unsubscribe
```

### 5. Testing with third party provider

**DISCLAIMER**: You can test the script by using a third party service if you wish. But be aware that you 
will be sending actual card data to a service for which Planview will take no responsibility. 

The recommendation is to **only set up webhooks towards servers that you yourself have full control over**. 
Only encrypted (e.g https://) are considered valid for webhooks in ProjectPlace.

If you understand the risks involved and still wish to test with a third party provider - 
such as https://webhook.site - follow this procedure - and take care to unsubscribe once done testing - since
webhooks will remain active and will continue to send data to the third party provider.

1. Navigate to https://webhook.site
2. You will be presented with a unique URL that will look something like this: 
   https://webhook.site/c2654750-fc30-4412-a6b1-fc81baaef070
3. Use this as your `--webhook-url` argument when setting up your subscription such as
   ```
   $ python3 board_subscription.py BOARD_ID --webhook-url https://webhook.site/c2654750-fc30-4412-a6b1-fc81baaef070
   ```
4. Once your subscription is in place - you can go to the board designated by BOARD_ID and move a card from one 
   column to another. Once it has been moved you should fairly instantly see a payload sent to your page on
   webhook.site.

