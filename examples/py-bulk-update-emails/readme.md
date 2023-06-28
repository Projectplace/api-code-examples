**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Bulk update emails of account users

This script showcases how to update the email-address of members of an enterprise account in bulk.

If an organisation changes its email domain, or has a new policy in regards to email user names, it
is good to prepare for that change in ProjectPlace by adding email-addresses to user accounts that
adhere to the new policy or domain.

For example. Say your organisation has the following naming scheme for e-mail addresses:

__John Doe (jdoe@organisation.org)__

And wish to change the naming scheme to

__john.doe@organisation.org__

Then it is possible to add this new email to the already existing user account as new primary email-address, so that
logins and authorisations are not disrupted. The already existing email will become a secondary email address for the
user.

The requirements however is that the domain `organisation.org` is enforced on your enterprise account. And
if changing domains - the new domain must also be enforced by your enterprise account. Contact support in order
to add domains to your account.

Please note that it is only possible to change the primary email of users whose

* Primary email is enforced by your account (the domain needs to be enforced by your account)
* Are not the owner of the account (only the account owner themselves can change their primary email)


### 1. Install requirements

See the `requirements.txt` file for needed third-party libraries.

You can install them by running `pip install -r requirements.txt`

### 2. Modify the script with your authorization attributes

The following section needs to be replaced with application key/secret and your OAuth1 token key/secret.

For this script it is recommended to use a robot account.

```
APPLICATION_KEY = 'REDACTED'
APPLICATION_SECRET = 'REDACTED'
ACCESS_TOKEN_KEY = 'REDACTED'
ACCESS_TOKEN_SECRET = 'REDACTED'
API_ENDPOINT = 'https://api.projectplace.com'
```

### 3. Run the script

```
$ python3 bulk_update_account_emails.py changes.csv
```

`changes.csv` has to be a comma separated file that maps up existing email-addresses to new email-addresses. 
Such as

```
jdoe@organisation.org,john.doe@organisation.org
bhall@organisation.org,belinda.hall@organisation.org
boboue@organisation.org,brent.oboue@newdomain.org
```

Where the left column represents existing email, and right column represents email-address to be added to the user
as a secondary email-address.

The script will then proceed to loop through all full account members of the account. Find all mentioned users.
It will then present a list of changes that are possible to conduct, if you confirm the operation -> the script
will then proceed to add the new primary email to each user account.

Finally the email-changes that were not possible to conduct are shown.
