const xlsx = require('node-xlsx');
const request = require('request');
const prompt = require('prompt-sync')();

const access_Token = prompt("Please provide your API access token: ");
const workspace_ID = prompt("Please provide the Workspace/Project ID where the Cards should appear in: ");
const file_Path = prompt("Please provide the full path to the xlsx file: ");
const work_Sheets = xlsx.parse(file_Path);

var failed_ImportedCards = [];

// Check how many Sheets there are in the xlsx file.
if (work_Sheets.length > 1) {
    console.warn("Found more than one sheet in the xlsx file.");
    sheet_Name = prompt("Please provide the sheet name that the Cards are in: ");
    handle_SheetInformation(get_SheetInformation(sheet_Name));
} else {
    handle_SheetInformation(work_Sheets[0]);
}

function get_SheetInformation(sheetName) {
    for (let i = 0; i < work_Sheets.length; i++){
        if ((work_Sheets[i].name).toLocaleLowerCase() == (sheetName).toLocaleLowerCase()) {
            return work_Sheets[i]
        }
    }
}
function handle_SheetInformation(sheet) {
    if (sheet.data[0].length < 2) {
        console.warn("Missing some attributes in the headers / top row of the sheet:", sheet.name);
        console.warn("Checking if it is the Board ID attribute...");
    }
    if (sheet.data[0].length > 13) {
        console.error("Too many attributes in the headers / top row of the sheet:", sheet.name);
        console.error("Found: "+sheet.data[0].length + " attributes, should be: 14");
        return false;
    }
    let userMappings = [];
    // Get the user headers in the xlsx file.
    for (let i = 0; i < sheet.data[0].length; i++) {
        // Check if one of the columns in the headers / top row is empty.
        if (sheet.data[0][i] == undefined) {
            console.error("The headers / top row has an empty column in position: ",i+1);
            return false;
        }
        userValue = sheet.data[0][i].toLowerCase();
        userMappings[userValue] = i;
    }
    
    // Remove the headers from the sheet data array so we only get the data for the Cards.
    sheet.data.splice(0,1);

    // Check for empty rows for each card that should be imported from the file.
    let filtered_sheet_data = [];
    sheet.data.forEach(Row => {
        if (!(Row.length == 0)) {
            filtered_sheet_data.push(Row);
        }
    });

    // Check if the user has Board ID in the headers / top row.
    if (userMappings["board id"] == undefined) {
        console.error("No 'board id' header found in the xlsx file.");
    }
    post_CreateCards(filtered_sheet_data,userMappings);

}
async function post_CreateCards(card_Information, userMappings) {
    /* 
    card_Information[y] = row
    card_Information[y][x] = in row y column x
    */
    let userMappings_keys = Object.keys(userMappings);
    let allUser_Cards = [];
    // Each row
    for (let i = 0; i < card_Information.length; i++) {
        let card = {}
        // Each column in that row
        for (let j = 0; j < card_Information[i].length; j++) {
            userMappings_keys.forEach(Key => {
                if (j == userMappings[Key]) {
                    card[Key] = card_Information[i][j];
                }
            });
        }
        allUser_Cards.push(card);
    }
    for (const Card of allUser_Cards) {
        // Check to see if the Card should be blocked.
        if (Card["blocked reason"] == undefined || Card["blocked reason"].length == 0 ) {
            // If the Card should not be blocked then set the attribute "is blocked" to 0 (false).
            Card["is blocked"] = 0;
        } else {
            // If the Card should be blocked then set the attribute "is blocked" to 1 (true).
            Card["is blocked"] = 1;
        }
        // Create the array for the checklist 
        let Card_CheckList = [];
        if (Card["checklist"] != undefined) {
            Card_CheckList = Card["checklist"].split("##");
        } 

        userMappings_keys.forEach(Key => {
            if (Card[Key] == undefined) {
                delete Card[Key];
            }
        });

        let full_Card = {
            assignee_id: Card["assignee"],
            block_reason: Card["blocked reason"],
            board_id: Card["board id"],
            checklist: Card_CheckList,
            column_id: Card["column"],
            description: Card["description"],
            due_date: Card["due date"],
            estimate: Card["points"],
            estimated_time: Card["estimated time"],
            is_blocked: Card["is blocked"],
            label_id: Card["label"],
            planlet_id: Card["activity"],
            title: Card["title"],
        }
        await send_Card(full_Card);
    }
    if (failed_ImportedCards.length > 0) {
        console.log();
        console.error("These Cards failed: ");
        console.log(failed_ImportedCards);
    }
}

async function send_Card(Card) {
    return new Promise(Information => {
        request.post("https://api.projectplace.com/1/projects/"+workspace_ID+"/cards/create-new", {
        auth: {
         "bearer": access_Token.toString(),
         "Content-Type": "application/json",
        },
        json: Card,
     }, function(error, response, body) {
        console.log(response.statusCode,response.statusMessage);
        if (response.statusCode != 200) {
            Card["Error"] = body
            failed_ImportedCards.push(Card);
            console.error(body);
        }
        Information(body);
     });
    });
}