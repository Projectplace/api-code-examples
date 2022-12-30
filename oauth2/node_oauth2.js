const config = {
    client: {
        id: '2f1b7f8dabf6b96d5a80244b14abd26d',
        secret: 'c813a96788efa524eb449e808b5991ec185457cf'
    },
    auth: {
        tokenHost: 'https://api.projectplace.com',
        tokenPath: '/oauth2/access_token',
        authorizeHost: 'https://api.projectplace.com',
        authorizePath: '/oauth2/authorize'
    }
};
const fs = require('fs')
const {AuthorizationCode} = require('simple-oauth2')
const prompt = require('prompt-sync')()
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));


async function run() {
    try {
        let accessTokenFileContents = fs.readFileSync(".access_token.json");
        await refreshToken(accessTokenFileContents)
    } catch (error) {
        if (error.code === "ENOENT") {
            await getAccessToken()
        }
    }

    let accessTokenFileContents = fs.readFileSync('.access_token.json')
    const client = new AuthorizationCode(config);
    let accessToken = client.createToken(JSON.parse(accessTokenFileContents))
    await getProfile(accessToken.token.access_token)
}

async function getProfile(accessToken) {
    fetch(
        'https://api.projectplace.com/1/user/me/profile', {
            headers: {'Authorization': `Bearer ${accessToken}`}
        }
    )
        .then((response) => response.json())
        .then((data) => console.log(data));
}

async function refreshToken(accessTokenFileContents) {
    const client = new AuthorizationCode(config);
    let accessToken = client.createToken(JSON.parse(accessTokenFileContents))

    console.log('Before refresh', accessToken)

    let refresh_question = prompt("Token has not expired, do you wish to renew it either way? y/n ");
    refresh_question = refresh_question.toLowerCase();
    if (refresh_question === "n") { return false}

    try {
        accessToken = await accessToken.refresh()
    } catch (e) {
        console.log(e)
    }
    console.log('After refresh', accessToken)

    fs.writeFileSync('.access_token.json', JSON.stringify(accessToken.token))
}

async function getAccessToken() {
    const client = new AuthorizationCode(config);

    const authorizationUri = client.authorizeURL({
        redirect_uri: 'https://compose.rnd.projectplace.com/omgomg',
        state: (Math.random() + 1).toString(36).substring(2)
    });

    console.log('Go to this URL and authorize the app:')
    console.log(authorizationUri)

    const authorizationCode = prompt('Paste the authorization code here:  ');

    const tokenParams = {
        code: authorizationCode,
    };

    const accessToken = await client.getToken(tokenParams);
    fetch(
        'https://api.projectplace.com/1/user/me/profile', {
            headers: {'Authorization': `Bearer ${accessToken.token.access_token}`}
        }
    ).then((data) => {
        console.log('Access token seems valid, saving to .access_token.json')
        fs.writeFileSync('.access_token.json', JSON.stringify(accessToken.token))
    }).catch((data) => {
        console.log(data)
    })
}


run()
