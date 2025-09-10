"""
pyesi-client:

SSO
"""

import base64
import hashlib
import secrets
import time
import urllib.parse

import jwt
from jwt import PyJWK
from pyesi_openapi import ApiClient, ApiException

from pyesi_client.constants import (
    DEFAULT_ESI_AUDIENCE,
    DEFAULT_ESI_ENDPOINTS_URL,
    DEFAULT_ESI_JWK_KID,
    EsiCodeChallengeMethod,
    EsiResponseType,
)
from pyesi_client.core.metadata_manager import JWK_TTL_DEFAULT, METADATA_TTL_DEFAULT, EsiMetadataManager
from pyesi_client.core.scope_manager import EsiScopeManager
from pyesi_client.models.auth_models import (
    EsiAuthorizationCodeRequest,
    EsiAuthorizationUrlData,
    EsiAuthorizationUrlParams,
    EsiBasicAuthHeaders,
    EsiPKCEResult,
    EsiRefreshTokenRequest,
    EsiRequestHeaders,
    EsiTokenPKCE,
)
from pyesi_client.models.token_models import (
    EsiJwtTokenData,
    EsiTokenResponse,
    EsiTokenSet,
)
from pyesi_client.models.jwk_models import EsiMetadataResponseEndpoints


class EsiAuth:
    def __init__(
        self,
        api_client: ApiClient,
        scope_manager: EsiScopeManager,
        redirect_uri: str,
        client_id: str,
        *,
        client_secret: str | None = None,
        metadata_endpoints_url: str = DEFAULT_ESI_ENDPOINTS_URL,
        metadata_ttl: int = METADATA_TTL_DEFAULT,
        jwks_ttl: int = JWK_TTL_DEFAULT,
        token_set: EsiTokenSet | None = None,
    ) -> None:
        self.api_client: ApiClient = api_client
        self.scope_manager: EsiScopeManager = scope_manager
        self.metadata_manager: EsiMetadataManager = EsiMetadataManager(
            api_client,
            metadata_endpoints_url=metadata_endpoints_url,
            metadata_ttl=metadata_ttl,
            jwks_ttl=jwks_ttl,
        )
        self._token_set: EsiTokenSet | None = token_set
        self.redirect_uri: str = redirect_uri
        self.client_id: str = client_id
        self.client_secret: str | None = client_secret
        self._pkce: EsiPKCEResult | None = None

    @property
    def endpoints(self) -> EsiMetadataResponseEndpoints:
        return self.metadata_manager.endpoints

    @property
    def issuer(self) -> str:
        return self.metadata_manager.issuer

    @property
    def _token_expired(self) -> bool:
        if not self._token_set:
            raise ValueError("No token set available")
        return int(time.time()) >= self._token_set.expires_at

    @property
    def access_token(self) -> str:
        if not self._token_set:
            raise ValueError("No token set available")
        if self._token_expired:
            self.refresh_token()
        return self._token_set.access_token

    @classmethod
    def _b64url_no_pad(cls, b: bytes) -> str:
        return base64.urlsafe_b64encode(b).decode().rstrip("=")

    @classmethod
    def _generate_pkce(cls) -> EsiPKCEResult:
        verifier = secrets.token_urlsafe(32)
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        challenge = cls._b64url_no_pad(digest)
        return EsiPKCEResult(verifier=verifier, challenge=challenge)

    def exchange_code(self, code: str) -> EsiTokenSet:
        """Exchange authorization code for tokens."""
        if not self.client_secret and not self._pkce:
            raise ValueError("PKCE required when no client secret provided")

        pkce = EsiTokenPKCE(client_id=self.client_id, code_verifier=self._pkce.verifier) if self._pkce else None
        request = EsiAuthorizationCodeRequest(code=code, pkce=pkce)

        self._token_set = self._request_token(request)
        return self._token_set

    def refresh_token(self, refresh_token: str | None = None) -> EsiTokenSet:
        """Refresh expired access token."""
        token = refresh_token or (self._token_set.refresh_token if self._token_set else None)
        if not token:
            raise ValueError("No refresh token available")

        if not self.client_secret:
            self._pkce = self._generate_pkce()

        pkce = EsiTokenPKCE(client_id=self.client_id, code_verifier=self._pkce.verifier) if self._pkce else None
        request = EsiRefreshTokenRequest(refresh_token=token, pkce=pkce)

        self._token_set = self._request_token(request)
        return self._token_set

    def verify_token(self, access_token: str | None = None) -> EsiJwtTokenData:
        """Verify JWT token and return decoded data."""
        token = access_token or self.access_token
        if not token:
            raise ValueError("No access token available")

        key = self.metadata_manager.get_jwk(DEFAULT_ESI_JWK_KID)
        if not key:
            raise ValueError("Cannot retrieve public key")

        data = jwt.decode(
            jwt=token,
            key=PyJWK(key.model_dump(), key.alg),
            issuer=self.issuer,
            audience=DEFAULT_ESI_AUDIENCE,
        )
        return EsiJwtTokenData.model_validate(data)

    def create_auth_url(self, *, state: str | None = None) -> EsiAuthorizationUrlData:
        """Generate authorization URL with optional PKCE."""
        if not self.client_secret:
            self._pkce = self._generate_pkce()

        params = EsiAuthorizationUrlParams(
            response_type=EsiResponseType.CODE,
            redirect_uri=self.redirect_uri,
            client_id=self.client_id,
            scope=self.scope_manager.to_oauth_string(),
            state=state or secrets.token_urlsafe(24),
            code_challenge=self._pkce.challenge if self._pkce else None,
            code_challenge_method=EsiCodeChallengeMethod.S256 if self._pkce else None,
        )
        url = f"{self.endpoints.authorization_endpoint}?{urllib.parse.urlencode(params.model_dump(exclude_none=True))}"
        return EsiAuthorizationUrlData(url=url, state=params.state)

    def _request_token(self, request: EsiAuthorizationCodeRequest | EsiRefreshTokenRequest) -> EsiTokenSet:
        """Make token request to OAuth endpoint."""
        headers = self._get_auth_headers()

        res = self.api_client.call_api(
            method="POST", url=self.endpoints.token_endpoint, header_params=headers, post_params=request.model_dump()
        )

        if res.status != 200:
            raise ApiException(res.status, res.data)

        token_response = EsiTokenResponse.model_validate_json(res.read())
        return EsiTokenSet.from_token_response(token_response)

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for token requests."""
        if self.client_secret:
            return EsiRequestHeaders(
                basic_auth_headers=EsiBasicAuthHeaders(client_id=self.client_id, client_secret=self.client_secret)
            ).model_dump()
        return EsiRequestHeaders().model_dump()
