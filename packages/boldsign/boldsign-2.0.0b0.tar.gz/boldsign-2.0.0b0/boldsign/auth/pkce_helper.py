import base64
import hashlib
import os
from boldsign.exceptions import ApiException

class PKCEHelper:
    """
    Utility class for generating PKCE (Proof Key for Code Exchange) codes.
    
    This generates:
    - A `code_verifier`: A high-entropy cryptographic random string.
    - A `code_challenge`: A SHA-256 hash of the `code_verifier`, encoded in a URL-safe format.
    
    These values are used in OAuth2 authentication flows to enhance security.
    """

    @staticmethod
    def generate_pkce_pair():
        """
        Generates a PKCE code_verifier and its corresponding code_challenge.

        :return: A tuple containing (code_verifier, code_challenge).
        """
        try:
            # Generate a secure random code_verifier (32-byte base64 URL-safe string)
            code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')

            # Generate the corresponding code_challenge (SHA-256 hash of code_verifier)
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode('utf-8')).digest()
            ).rstrip(b'=').decode('utf-8')

            return code_verifier, code_challenge
        except Exception as e:
            raise ApiException(500, f"PKCE generation failed: {str(e)}") from e
