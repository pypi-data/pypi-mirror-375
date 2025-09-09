import logging
from typing import Any, Optional
from dotenv import load_dotenv
import httpx
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.common.enums import AI_UTILITIES_ENDPOINTS


load_dotenv()


class AiUtilities(BaseService):
    """
    Utility class for cryptographic operations required by AI services, such as encryption of payloads
    and loading public keys from X.509 certificates.

    This class is intended to be used internally by AI-related service classes to ensure secure
    transmission of sensitive healthcare data to backend APIs.

    !!! note "Key Features"
        - Loads RSA public keys from PEM-encoded X.509 certificates and converts them to JWK format.
        - Encrypts arbitrary payloads using JWE (JSON Web Encryption) with RSA-OAEP-256 and AES-GCM.
        - Handles environment variable management for encryption keys.
        - Provides robust error handling and logging for all cryptographic operations.

    Methods:
        load_public_key_from_x509_certificate : Loads an RSA public key from a PEM-encoded X.509 certificate and returns it as a JWK dictionary.
        encryption : Encrypts a payload dictionary using JWE with an RSA public key loaded from the `ENCRYPTION_PUBLIC_KEY` environment variable.

    Example usage:
        ```
        utils = AiUtilities()
        encrypted = await utils.encryption({"foo": "bar"})
        ```
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    
    async def encryption(self, payload: dict[str, Any], public_key: Optional[str] = None) -> dict:
        """
        Calls the remote NestJS service to encrypt a payload using JWE.

        This method sends the plain payload dictionary to the `/encrypt` endpoint,
        along with an optional public key.

        ### Args:
            payload (Dict[str, Any]): The data to be encrypted.
            public_key (Optional[str]): An optional PEM-encoded public key to use for encryption.

        ### Returns:
            str: The JWE compact-serialized encrypted string returned by the service.

        ### Raises:
            RuntimeError: If the request to the encryption service fails or the service returns an error status.

        Example:
            ```
            utils = AiUtilities()
            encrypted_payload = await utils.encryption({"foo": "bar"})
            print(encrypted_payload)
            # Output: eyJhbGciOiJSU0EtT0FFUC0yNTYiLCJlbmMiOiJBMTI4R0NN...
            ```
        """

        request_body = {
            "input": payload
        }
        if public_key:
            request_body["key"] = public_key

        try:
            response = await self.post(
                AI_UTILITIES_ENDPOINTS.ENCRYPTION,
                request_body,
                response_model=dict 
            )
            return response

        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"Encryption service returned an error: {e.response.status_code} - {e.response.text}",
                exc_info=True
            )
            raise RuntimeError(f"Encryption failed with status {e.response.status_code}") from e

        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred during encryption call: {e}",
                exc_info=True
            )
            raise RuntimeError(f"An unexpected error occurred: {e}") from e  
    
    async def decryption(self, encrypted_data: str, private_key: Optional[str] = None) -> dict:
        """
        Calls the remote NestJS service to decrypt a JWE payload.

        This method sends an encrypted JWE string to the `/decrypt` endpoint.
        It mirrors the structure of the NestJS controller, accepting the encrypted
        payload and an optional private key.

        ### Args:
            encrypted_data (str): The JWE compact-serialized string to be decrypted.
            private_key (Optional[str]): An optional PEM-encoded private key. If provided,
                it will be sent to the decryption service. Otherwise, the service
                will use its default key.

        ### Returns:
            Any: The decrypted payload returned from the service.

        ### Raises:
            RuntimeError: If the request to the decryption service fails or the
                          service returns an error status.

        Example:
            ```
            utils = AiUtilities()
            encrypted_jwe = "eyJhbGciOiJSU0EtT0FFUC0yNTYiLCJlbmMiOiJBMTI4R0NN..."
            decrypted_payload = await utils.decryption(encrypted_jwe)
            print(decrypted_payload)
            # Output from service: {'patientName': 'John Doe', 'diagnosis': 'Hypertension'}
            ```
        """
        request_body = {
            "payload": {"data": encrypted_data}
        }
        if private_key:
            request_body["key"] = private_key

        try:
            response = await self.post(AI_UTILITIES_ENDPOINTS.DECRYPTION,request_body,response_model= dict )
            return response
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Decryption service returned an error: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise RuntimeError(f"Decryption failed with status {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during decryption call: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred: {e}") from e
