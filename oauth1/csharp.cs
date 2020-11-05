using System;
using DevDefined.OAuth.Consumer;
using DevDefined.OAuth.Framework;
using Newtonsoft.Json;

namespace oauth1robot
{
    public class Profile
    {
        public int id { get; set; }
        public String first_name { get; set; }
        public String last_name { get; set; }
    }

    class MainClass
    {
    	public static void Main(string[] args)
    	{
            string requestTokenUrl = "https://api.projectplace.com/initiate";
            string authorizationUrl = "https://api.projectplace.com/authorize";
            string tokenUrl = "https://api.projectplace.com/token";
            string apiEndpoint = "https://api.projectplace.com";
            string consumerKey = "APPLICATION_KEY_GOES_HERE";
            string consumerSecret = "APPLICATION_SECRET_GOES_HERE";
            IToken accessToken = null;

            // 1. If you already have an access token - uncomment this section and enter it here.
            //IToken accessToken = new TokenBase();
            //accessToken.Token = "ACCESS_TOKEN_KEY_GOES_HERE";
            //accessToken.TokenSecret = "ACCESS_TOKEN_SECRET_GOES_HERE";
            
            // 2. Create the consumer context
            OAuthConsumerContext consumerContext = new OAuthConsumerContext
            {
                ConsumerKey = consumerKey,
                ConsumerSecret = consumerSecret,
                SignatureMethod = SignatureMethod.HmacSha1,
                UseHeaderForOAuthParameters = true,
            };

            // 3. Start session
            OAuthSession session = new OAuthSession(consumerContext, requestTokenUrl, authorizationUrl, tokenUrl);

            // 4. If you do not have an access token, you will first have to authorize
            // access. In this part we formulate a URI which you must open in a web-broser.
            // Once you have completed the log-in and accepted access for the application
            // You will be redirected to whatever page is in the applications callback
            // Simply check the URL and look for the oauth_verifer parameter, and copy that
            if (accessToken == null) {
                IToken requestToken = session.GetRequestToken();

                string authorizationLink = session.GetUserAuthorizationUrlForToken(requestToken);

                Console.WriteLine("Authorize this application by going to {0}", authorizationLink);
                Console.WriteLine("Then enter the oauth_verifier here:");
                string verificationCode = Console.ReadLine();

                accessToken = session.ExchangeRequestTokenForAccessToken(requestToken, verificationCode);
                Console.WriteLine("Here is your new access token: {0} with secret: {1}\n", accessToken.Token, accessToken.TokenSecret);
            }

            // 5. We have an access token - assign it to the session    
            session.AccessToken = accessToken;

            // 6. Lets ask for a protected resource, such as your own profile
            string responseText = session.Request().Get().ForUrl(apiEndpoint + "/1/user/me/profile").ToString();
            Profile profile = JsonConvert.DeserializeObject<Profile>(responseText);
            Console.WriteLine("Successfully fetched profile for {0} {1}", profile.first_name, profile.last_name);
        }
    }
}
