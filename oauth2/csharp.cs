using System;
using Newtonsoft.Json;
using System.Net.Http;
using System.Net;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.IO;

namespace oauth2
{
    public class Profile
    {
        public int id { get; set; }
        public String first_name { get; set; }
        public String last_name { get; set; }
        public String email { get; set; }
    };

    public class AccessToken
    {
        public String token_type {get; set;}
        public String access_token {get; set;}
        public String expries {get; set;}
        public String refresh_token {get; set;}
    }


    class MainClass
    {
        private static string redirectUri = "REDACTED";  // Check your app settings
        private static string clientId = "REDACTED";     // Check your app settings
        private static string clientSecret = "REDACTED"; // Check your app settings
        private static HttpClient _httpClient = new HttpClient();
        private static string baseUri = "https://api.projectplace.com";
        private static string authUrl = baseUri + "/oauth2/authorize";
        private static string tokenUrl = baseUri + "/oauth2/access_token";
        private static Random rand = new Random();
        private static AccessToken accessToken;

        /*
            Checks if an access token is stored to disk (in .atoken.json). If so, attempts to check if it is still
            valid (by asking for the user profile). If it isn't valid: tenatively invokes "refreshAccessToken", to
            see if the access token is still "refreshable".
        */
        public static void ensureAccessToken() {
            try {
                using (StreamReader file = File.OpenText(@".atoken.json"))
                {
                    JsonSerializer serializer = new JsonSerializer();
                    accessToken = (AccessToken)serializer.Deserialize(file, typeof(AccessToken));
                }

            // No access token on disk - abort
            } catch (FileNotFoundException) {
                return;
            }

            // Lets see if the access token is valid
            if (accessToken.access_token is not null) {
                Console.WriteLine("We have an access token, lets see if it is still valid, otherwise refresh it");

                Profile profile = profileRequest().Result;

                if (profile is null) {
                    Console.WriteLine("Seems like the access token has expired - lets attempt refreshing it");

                    refreshAccessToken();
                }
            }
        }

        /*
            Stores the access token in a local file (.atoken.json)
        */
        public static void storeAccessToken() {
            // Store access token locally
            using (StreamWriter file = File.CreateText(@".atoken.json"))
            {
                JsonSerializer serializer = new JsonSerializer();
                serializer.Serialize(file, accessToken);
            }
        }

        /*
            Attempts to refresh the access token - an access token is "refreshable" for two weeks.
        */
        public static async void refreshAccessToken()
        {
            var values = new Dictionary<string, string>
                {
                    { "client_id", clientId },
                    { "client_secret", clientSecret },
                    { "refresh_token", accessToken.refresh_token },
                    { "grant_type", "refresh_token" }
                };

            var requestBody = new FormUrlEncodedContent(values);
            var response = await _httpClient.PostAsync(tokenUrl, requestBody);
            if (response.IsSuccessStatusCode) {
                var contents = await response.Content.ReadAsStringAsync();
                accessToken = JsonConvert.DeserializeObject<AccessToken>(contents);
                storeAccessToken();
            }
        }


        /*
            Initial access token exchange - this should normally only happen once - provided that
            this script is run at least once every two weeks.
        */
        public static async void accessTokenRequest(string verificationCode)
        {
            var values = new Dictionary<string, string>
                {
                    { "client_id", clientId },
                    { "client_secret", clientSecret },
                    { "code", verificationCode },
                    { "grant_type", "authorization_code"}
                };

            var content = new FormUrlEncodedContent(values);
            var response = await _httpClient.PostAsync(tokenUrl, content);
            var contents = await response.Content.ReadAsStringAsync();

            accessToken = JsonConvert.DeserializeObject<AccessToken>(contents);

            storeAccessToken();
        }

        /*
            Returns a request message usable by httpClient for the purpose of a simple GET request
            using a valid access token.
        */
        public static HttpRequestMessage ApiGetRequest(string uri)
        {
            return new HttpRequestMessage
            {
                Method = HttpMethod.Get,
                RequestUri = new Uri(baseUri + uri),
                Headers = {
                    { HttpRequestHeader.Authorization.ToString(), String.Format("Bearer {0}", accessToken.access_token)},
                    { HttpRequestHeader.Accept.ToString(), "application/json" },
                }
            };
        }

        /*
            Example of an API request - in this case invoking api.projectplace.com/1/user/me/profile which returns
            basic data about a user.
        */
        public static async Task<Profile> profileRequest()
        {
            var httpRequestMessage = ApiGetRequest("/1/user/me/profile");

            var response = await _httpClient.SendAsync(httpRequestMessage);
            if (response.IsSuccessStatusCode) {
                var responseContents = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Profile>(responseContents);
            }

            return null;
        }

    	/*
            Script entry point
        */
        public static void Main(string[] args)
    	{
            ensureAccessToken();

            /* In the first run - you will not have an access token stored - and will always end up in this if-statement */
            if (accessToken is null) {
                string randomState = rand.Next(999999999).ToString();
                string readyAuthUrl = String.Format("{0}?client_id={1}&state={2}&redirect_uri={3}", authUrl, clientId, randomState, redirectUri);
                Console.WriteLine("Authorize this application by going to {0}", readyAuthUrl);
                Console.WriteLine("Enter verification code here (hint: look in the address bar of the browser for the code parameter):");
                string verificationCode = Console.ReadLine();
                accessTokenRequest(verificationCode);
            }
            Profile profile = profileRequest().Result;
            Console.WriteLine("Successfully fetched profile for {0} {1} ({2})", profile.first_name, profile.last_name, profile.email);
        }
    }
}