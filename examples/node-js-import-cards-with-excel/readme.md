**Disclaimer**: Planview provides these examples for instructional purposes. While you are welcome to use this
code in any way you see fit - Planview does not accept any liability or responsibility for you choosing to do so.

# Upload Cards from Xlsx file

This NodeJS script reads the provided Xlsx file and creates Cards to the correct Board/Activity.
The script requires a Oauth2 token in order to make the API calls to create the Cards, 
it will assume that you have already created one.

#### 1. Install requirements
See the `package.json` file for the needed third-party libraries.

#### 2. Run the script
```
node Import_Cards_From_Xlsx.js 
```

#### 3. Provide the necessary information
* The script will ask first for your access token (Oauth2 token).
* Then it will ask for the Workspace ID of where Board that you have provided in the Xlsx is located.
* Lastly the script will ask the exact path for the Xlsx file.

##### Note file name location
If the Xlsx file is in `c:/User` folder, then you should provide the path as: `c:/user/FILENAME.xlsx`.

##### See the test Xlsx file named: ```nodejs_cards.xlsx```

The following headers are possible to use in your Excel-file:
Headers that will be used: **Due date, Description, Assignee, Title, Label, Points, Estimated time, 
Blocked reason, Column, Checklist, Co-assignees, Activity, Board id.**

If you have more headers that are not on the list above, then they will be ignored.

***The headers does not have to be arranged in any specific order for the script to work.***


1. The script will get all the headers from the Xlsx file.
2. Create a JSON object for each of the Cards.
3. Lastly it will send the JSON object to the API endpoint: ```/cards/create-new``` - once for every
   card
4. If any of the Cards failed to import then you will see those Cards in the console once the script is done.

