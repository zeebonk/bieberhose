import click
from requests_oauthlib.oauth1_session import OAuth1, OAuth1Session, TokenRequestDenied

from . import credentials


@click.command()
@click.option(
    "--consumer-key",
    help="Consumer key for accessing the Twitter API.",
    envvar="CONSUMER_KEY",
    required=True,
)
@click.option(
    "--consumer-secret",
    help="Consumer secret for accessing the Twitter API.",
    envvar="CONSUMER_SECRET",
    required=True,
)
def authenticate(consumer_key, consumer_secret):
    """
    Authenticate against the Twitter API
    """

    # This implements the so called PIN-Based OAuth flow as described here:
    # https://developer.twitter.com/en/docs/basics/authentication/overview/pin-based-oauth

    if credentials.exists():
        click.confirm(
            "This will overwrite existing credentials, are you sure?", abort=True
        )

    # Step 1: fetch a request token
    oauth = OAuth1Session(consumer_key, consumer_secret)
    try:
        request_token_response = oauth.fetch_request_token(
            "https://api.twitter.com/oauth/request_token?oauth_callback=oob"
        )
    except TokenRequestDenied:
        raise click.ClickException("Invalid consumer secret/consumer key combination")

    # Step 2: get an authorization url and ask user to enter the PIN
    authorization_url = oauth.authorization_url(
        "https://api.twitter.com/oauth/authorize"
    )
    pin = input(
        "In order to authenticate, go to the following URL, "
        "authorize the app and copy the PIN:\n"
        f"{authorization_url}\n"
        "Enter PIN: "
    )

    # Step 3: get an access token using the PIN
    oauth = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=request_token_response["oauth_token"],
        resource_owner_secret=request_token_response["oauth_token_secret"],
        verifier=pin,
    )
    try:
        access_token_response = oauth.fetch_access_token(
            "https://api.twitter.com/oauth/access_token"
        )
    except TokenRequestDenied:
        raise click.ClickException("Entered PIN is invalid")

    # Create new OAuth1 instance that can be used by the `requests` library for
    # authenticating requests and store it for later use.
    credentials.save(
        OAuth1(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token_response["oauth_token"],
            resource_owner_secret=access_token_response["oauth_token_secret"],
        )
    )

    print("Authentication saved, bieberhose is ready to go! 🚀")
