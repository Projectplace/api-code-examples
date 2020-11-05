require 'launchy'
require 'oauth2'
require 'net/http'
require 'uri'
require 'json'

client_id = 'ENTER_CLIENT_ID_HERE'
client_secret = 'ENTER_CLIENT_SECRET_HERE'
redirect_url = 'ENTER_REDIRECT_URL_AS_SPECIFIED_IN_APP_HERE'
api_endpoint = 'https://api.projectplace.com'
authorize_url = '/oauth2/authorize' # Relative to api_endpoint
token_url = '/oauth2/access_token'

client = OAuth2::Client.new(client_id, client_secret, :site => api_endpoint)

# Open a webbrowser to start the authorisation process.
Launchy.open(api_endpoint + authorize_url + '?client_id=' + client_id + '&redrect_url=' + redirect_url)

# Once completed the browser will redirect, grab the "code" parameter from the URL and enter here
# Normally you would end up in your own callback where you can grab the "code" programatically
puts "Enter code"

code = gets.chomp

# Request access token
response = Net::HTTP.post_form(URI.parse(api_endpoint + token_url), {
  "client_id" => client_id,
  "client_secret" => client_secret,
  "code" => code,
  "grant_type" => "authorization_code"
})

token_response = JSON.parse(response.body)

token = OAuth2::AccessToken.from_hash(client, token_response)

# Issue an API request using the access token, and pretty print it.
profile_response = token.get('/1/user/me/projects')
puts JSON.pretty_generate(JSON.parse(profile_response.body))

