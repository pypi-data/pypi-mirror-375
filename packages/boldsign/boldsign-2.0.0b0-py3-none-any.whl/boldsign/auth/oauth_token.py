from datetime import datetime, timedelta

class OAuthToken:
    """
    Represents an OAuth token response, storing access token details
    and calculating the expiration time.
    """

    def __init__(self, access_token, token_type, expires_in, refresh_token = None, scope = None):
        """
        Initializes an OAuthTokenResponse instance.

        :param access_token: The access token received from the OAuth server.
        :param token_type: The type of token (usually 'Bearer').
        :param expires_in: Lifetime of the access token in seconds.
        :param refresh_token: (Optional) The refresh token for obtaining a new access token.
        """
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.scope = scope

    @classmethod
    def from_response(cls, response_json):
        """
        Creates an OAuthTokenResponse instance from a JSON response.

        :param response_json: Dictionary containing OAuth token response data.
        :return: OAuthTokenResponse instance.
        :raises ValueError: If required fields are missing in the response.
        """
        if not response_json.get("access_token") or not response_json.get("expires_in"):
            raise ValueError("Invalid response: 'access_token' and 'expires_in' are required.")

        return cls(
            access_token=response_json.get("access_token"),
            token_type=response_json.get("token_type"),
            expires_in=response_json.get("expires_in"),
            refresh_token=response_json.get("refresh_token"),
            scope = response_json.get('scope')
        )