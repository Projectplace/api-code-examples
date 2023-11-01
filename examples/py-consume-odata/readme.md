**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Consume from ODATA endpoint using OAuth2

This script demos how you can call OData endpoints.

Our OData endpoint is https://odata3.projectplace.com and supports three different categories

* `https://odata3.projectplace.com/pm` for Workspace related data,
* `https://odata3.projectplace.com/am` for Account related data and
* `https://odata3.projectplace.com/portfolios` for Portfolios related data

Each of these endpoints contains different entity-sets which can be consumed via normal API authentication,
just as with calls to the `https://api.projectplace.com` URL. The only thing that is required is an OAuth1 or
OAuth2 access token with relevant access rights.


**Workspace related data**
Call https://odata3.projectplace.com/pm/ENTITY_SET

Where `ENTITY_SET` is one of the following:

1. `Cards`
2. `Activities`
3. `TimeReports`
4. `CardCustomFields`
5. `ActivityCustomFields`
6. `Members`
7. `Workspaces`
8. `WorkspaceMemberships`
9. `WorkspaceMemberRoles`
10. `CardsCoAssignees`
11. `CardTags`
12. `IssueTags`
13. `PlanSnapshots`
14. `PlanSnapshotValues`
15. `Issues`

**Account related data**
Call https://odata3.projectplace.com/am/ENTITY_SET

Where `ENTITY_SET` is one of the following:

1. `AccountPeople`
2. `AccountWorkspaces`
3. `AccountWorkspaceMembers`
4. `Requests`
5. `WorkspaceCustomField`
6. `RequestCustomFormFields`

**Portfolios related data**
Call https://odata3.projectplace.com/portfolios/ENTITY_SET

Where `ENTITY_SET` is one of the following

1. `Portfolios`
2. `PortfolioWorkspaces`
3. `KPIStatusReports`

In this script we have opted to demonstrate calling the OData endpoints using the OAuth2 client credentials flow.

The client credentials flow for OAuth2 only works for robot accounts. For any other user you would have
to acquire a valid OAuth1 or OAuth2 access token. Keep this in mind for your own implementation or integration.


### 1. Install requirements

See the `requirements.txt` file for needed third-party libraries.

You can install them by running `pip install -r requirements.txt`

### 2. Modify the script with your authorization attributes

The following section needs to be replaced with application key/secret for your account robot. You CAN call 
the endpoints as a normal user as well but will have to obtain an access token from them as individuals.

```
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
```

### 3. Run the script

```
$ python3 consume_odata.py
```

The script will first ask you which endpoint you want to consume:

```
The following ODATA collections are available
 1. Workspace data
 2. Account data
 3. Portfolio data
Which would you like to investigate? (1, 2, 3):
```

If you pick "2" the you will be further presented with a list of entity sets that are available on that
endpoint:

```
The following entity sets are available for Account data:
1. AccountPeople
2. AccountWorkspaces
3. AccountWorkspaceMembers
4. Requests
5. WorkspaceCustomField
6. RequestCustomFormFields
Which entity set would you like to download?
```

If you pick "2" - a download of "AccountWorkspaces" will commence, and the prompt will give you information about
how much data is being downloaded. It cannot give you an estimate of when it is done, because the data is being
streamed back.

```
Downloading am/AccountWorkspaces please wait... 1.21 MB
```

Once done, the contents will have been downloaded in a compressed file.

```
Done! Downloaded 5.86 MB to am_AccountWorkspaces_2023-10-30.json.gz (Final file size: 1.08 MB)
```

If you are on a windows machine you may want to use WinZip or similar to extract the contents, while Macs and 
Linux-machines can handle *.gz compression out of the box.

