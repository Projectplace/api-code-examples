/*
This script show cases the OAuth2 flow using Node JS.
To test the script you must first have an application registered with ProjectPlace.
You also need to have the "simple-oauth2", "prompt.sync" libraries installed.
Run the script with:
    node .\node.js
The first thing that will happen is that the script will ask you for your Client ID and Client Secret,
They may look like this 0833dea4f3ffffff1e6295ac1b3d3e08 deded29dba64fffffa20aa4acae81166addda836.
Then it will ask you for your application redirect URI.
In the console you will then see a link, open this link in your web browser, this will prompt you to authenticate the application.
You will then be redirected to the redirect URI, in the URI there will be a code attribute.
Copy that attribute to the terminal as prompted.
The script will test and see if the Token is valid by calling the profile API.
Now you should have a file called "access_token.json" with your access Token inside.

NOTE:
This code needs to run on Node JS version 18 or higher that supports the Fetch API.
You might get this in the Terminal:
    ExperimentalWarning: The Fetch API is an experimental feature. This feature could change at any time
    (Use `node --trace-warnings ...` to show where the warning was created)
This is normal.
*/

const { AuthorizationCode } = require('simple-oauth2')
const prompt = require('prompt-sync')();
const FS = require("fs");

const accessToken_Headers = new Headers();

const config = {
    client: {
        id: prompt("Client ID: "),
        secret: prompt("Client Secret: ")
    },
    auth: {
        tokenHost: 'https://api.projectplace.com',
        tokenPath: '/oauth2/access_token',
        authorizeHost: 'https://api.projectplace.com',
        authorizePath: '/oauth2/authorize'
    }
}

async function refresh_Token(accessTokenFileContents) {
    if ("refresh_token" in JSON.parse(accessTokenFileContents)) {
        const client = new AuthorizationCode(config);
        
        let accessToken = client.createToken(JSON.parse(accessTokenFileContents));
        if (accessToken.expired()) {
            accessToken = await accessToken.refresh();
            checkAccessToken(accessToken);
        } else {
            refresh_question = prompt("Token has not expired, do you wish to renew it either way? y/n: ");
            refresh_question = refresh_question.toLowerCase();
            if (refresh_question == "n") { return false}
            console.log("Before Refresh: ", accessToken);
            
            try {
                accessToken = await accessToken.refresh();    
            } catch (error) {
                console.log(error);
            }
            checkAccessToken(accessToken);
        }
    } else {
        console.log("Missing 'refresh_token' in access_token.json - creating a new Token");
        get_Access_Token()
    }
}

async function get_Access_Token() {
    const client = new AuthorizationCode(config);

    const redirect_uri = prompt("Application redirect URI: ")
    
    const authorizationUri = client.authorizeURL({
        redirect_uri: redirect_uri,
        state: ''
    });

    console.log('Go to this URL and authorize the app:')
    console.log(authorizationUri)

    const authorizationCode = prompt('Paste the authorization code here: ');

    const tokenParams = {
        code: authorizationCode,
        redirect_uri: redirect_uri,
    };
    const accessToken = await client.getToken(tokenParams);
    checkAccessToken(accessToken)
}

async function checkAccessToken(accessToken) {
    accessToken_Headers.append("Authorization", "Bearer " + accessToken.token.access_token);
    const response = await fetch("https://api.projectplace.com/1/user/me/profile", {"headers": accessToken_Headers})
    .then((data) => {
        console.log("Access token seems valid, saving to -> acess_token.json");
        console.log("Access token: ", accessToken.token.access_token);
        FS.writeFileSync("access_token.json", JSON.stringify(accessToken));
    })
    .catch((data) => {
        console.log(data);
    })
    
    return response;
}

async function run() {
    try {
        let accessTokenFileContents = FS.readFileSync("access_token.json");
        await refresh_Token(accessTokenFileContents);
    } catch (error) {
        if (error.code === "ENOENT") {
            await get_Access_Token();
        }
    }
}

run();