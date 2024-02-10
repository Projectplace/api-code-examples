**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Rename columns from something to something else

This script showcases how to enforce a certain naming structure to a certain column order in all boards
in all workspaces in an account.

For example.

1. Say most boards in your account start with a column named "Planned"
2. You want to ensure that all first columns in all boards are named "Backlog"

The recipie to accomplish this is trivial but involves a few steps.

1. First we must find all workspaces in your account
2. Then we must find all boards in each workspace in turn
3. In each board we check what the column's name is - and if it isn't "Planned" we rename it.

### 1. Install requirements

See the `requirements.txt` file for needed third-party libraries.

You can install them by running `pip install -r requirements.txt`

### 2. Modify the script with your authorization attributes

The following section needs to be replaced with application key/secret and your Robot account 
client ID and client secret.

```
CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'
```

### 3. Run the script

```
$ python3 enforce_column_names.py COLUMN_POSITION NEW_NAME -o OPTIONAL_FROM_NAME
```

* `COLUMN_POSITION` is the zero-indexed position of the column you want to enforce a new name on (the left-most column
  has position `0`)
* `NEW_NAME` is the new name of the column that you want to enforce
* `-o OPTIONAL_FROM_NAME` is an optional parameter - and will enforce `NEW_NAME` only if the current name of the column 
  currently is `OPTIONAL_FROM_NAME`. In this way you can specify that you want to rename a certain column to the new 
  name only if it has a certain name at the moment.

Example 1. Rename the second column in all boards to "In Progress"

```
$ python3 enforce_column_names.py 1 "In Progress"
```

Example 2. Rename the first column in all boards to "Backlog" only if the current name is "Planned"

```
$ python3 enforce_column_names.py 0 "Backlog" -o "Planned"
```
