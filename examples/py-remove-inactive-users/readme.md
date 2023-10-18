**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Remove inactive users from ProjectPlace

This script showcases how to delete ProjectPlace (alternatively remove them from your account)
after a period of inactivity.

Removing users is generally straightforward. However, there are a number of things to take into consideration.

1. External members cannot be deleted - they can only be removed from access to your account. (External members
   are defined as users who are members of at least one of your account's workspaces, but are not themselves members
   of your account).
2. You cannot delete members from your account if they are head administrators of Workspaces, Workspace Templates,
   Portfolios or Teams. Unless you first reassign their head admin roles to someone else. Fortunately our APIs allow
   for this in one and the same call.

This script takes as input:

* How many days a user needs to have NOT logged in, in order to be considered "inactive". The limit here is up to
  your discretion, typically a person who has not logged in for 180 days can definitely be considered inactive.
* Who to reassign head admin roles to for the users you decide to delete or remove from your account.


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

### 3. Run the script

```
$ python3 remove_inactive_users.py DAYS NEW_HEAD_ADMIN_ID
```

Where `DAYS` is the number of allowed days between logins before being considered "inactive". `NEW_HEAD_ADMIN_ID` refers
to the user ID of an account member who should take over the head admin roles that will be left vacant as you proceed
with the script.

Invoking this script will print out inactive users. If they are head administrators of any Workspaces, Workspace
Templates, Portfolios or Teams, these will also be listed. Finally, for each individual determined by the script
to be inactive you will be asked to verify that you do indeed want to delete or remove them, along with a notice
about who their vacated head admin roles will go to.
