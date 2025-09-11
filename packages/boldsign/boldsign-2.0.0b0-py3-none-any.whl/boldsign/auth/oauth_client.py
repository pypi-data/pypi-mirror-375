from enum import Enum
from urllib.parse import urlencode
import requests
from .oauth_token import OAuthToken
from boldsign.exceptions import ApiException
from .pkce_helper import PKCEHelper

class Region(Enum):
        US = "https://account.boldsign.com"
        EU = "https://account-eu.boldsign.com"
        CA = "https://account-ca.boldsign.com"

class OAuthClient:
    """
    Helper class for handling OAuth2 authentication flows in the BoldSign SDK.
    
    Provides methods to:
    - Generate the authorization URL (PKCE flow).
    - Exchange an authorization code for access and refresh tokens.
    - Refresh an expired access token.
    - Authenticate using client credentials.
    """
    AUTH_URL = Region.US.value
    code_verifier, code_challenge = PKCEHelper.generate_pkce_pair()
    def __init__(self, client_id, client_secret , scope = None, redirect_uri = None, state = None,region = None,code_verifier = None, code_challenge = None):

        """
        Initializes OAuthClient with required credentials.
        
        :param client_id: OAuth client ID.
        :param client_secret: OAuth client secret (optional).
        :param scope: Scope of permissions requested (optional).
        :param redirect_uri: Redirect URI for authorization flow (optional).
        :param code_challenge: Code challenge for PKCE flow (optional).
        :param code_verifier: Code verifier for PKCE flow (optional).
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self.region = region.value if region else None
        self.code_verifier = code_verifier
        self.code_challenge = code_challenge
    def _handle_response(self, response):

        """
        Handles API responses, raises exceptions for errors.

        :param response: The HTTP response object.
        :return: Parsed OAuthToken object.
        :raises ApiException: If an error occurs in the response.
        """

        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            error_message = f"Failed to parse JSON response. Status: {response.status_code}, Reason: {response.reason}, Content: {response.text}"
            raise ApiException(response.status_code, error_message)
        
        if "error" in response_json:
            raise ApiException(response.status_code, response)
        
        return OAuthToken.from_response(response_json)

    def get_authorization_url(self, state=None):
        if self.code_challenge is None:
            self.code_challenge = OAuthClient.code_challenge
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state":state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256"
        }
        if state is not None:
            params["state"] = state
        if self.region is None:
            region = OAuthClient.AUTH_URL
        else:
            region = self.region
        return f"{region}/connect/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        
        """
        Exchanges an authorization code for access and refresh tokens.

        :param code: Authorization code received from the authorization flow.
        :param token_endpoint: Custom base URL for token exchange (optional).
        :param code_verifier: PKCE code verifier (optional).
        :return: OAuthToken containing access and refresh tokens.
        :raises ApiException: If an error occurs during token exchange.
        """
        if self.code_verifier is None:
            self.code_verifier = OAuthClient.code_verifier
        payload = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': self.code_verifier
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        if self.region is None:
            region = OAuthClient.AUTH_URL
        else:
            region = self.region
        response = requests.post(f'{region}/connect/token', data = payload, headers = headers)
        return self._handle_response(response)
    
    def refresh_access_token(self, refresh_token):

        """
        Refreshes the access token using a valid refresh token.

        :param refresh_token: Refresh token received during authentication.
        :param token_endpoint: Custom base URL for token refresh (optional).
        :return: OAuthToken containing the new access token.
        :raises ApiException: If the refresh token is invalid or expired.
        """

        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        if self.region is None:
            region = OAuthClient.AUTH_URL
        else:
            region = self.region
        response = requests.post(f'{region}/connect/token', data = payload, headers = headers)
        return self._handle_response(response)
    
    def get_token_with_client_credentials(self):

        """
        Authenticates using the client credentials grant type.

        :param token_endpoint: Custom base URL for token request (optional).
        :return: OAuthToken containing the access token.
        :raises ApiException: If the client credentials are invalid.
        """

        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        if self.region is None:
            region = OAuthClient.AUTH_URL
        else:
            region = self.region
        response = requests.post(f'{region}/connect/token', data = payload, headers = headers)

        return self._handle_response(response)
