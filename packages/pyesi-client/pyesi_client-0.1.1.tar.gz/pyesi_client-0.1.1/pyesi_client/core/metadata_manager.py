"""
pyesi-client:

SSO Metadata Manager
"""

import time

from pyesi_openapi import ApiClient

from pyesi_client.constants import DEFAULT_ESI_ENDPOINTS_URL
from pyesi_client.models import EsiJwk, EsiJwksResponse, EsiMetadataResponse, EsiMetadataResponseEndpoints

METADATA_TTL_DEFAULT = 2592000  # 24 * 60 * 60 * 30
JWK_TTL_DEFAULT = 86400  # 24 * 60 * 60


class EsiMetadataManager:
    def __init__(
        self,
        api_client: ApiClient,
        *,
        metadata_endpoints_url: str = DEFAULT_ESI_ENDPOINTS_URL,
        metadata_ttl: int = METADATA_TTL_DEFAULT,
        jwks_ttl: int = JWK_TTL_DEFAULT,
    ) -> None:
        self.api_client: ApiClient = api_client
        self.metadata_endpoints_url: str = metadata_endpoints_url
        self.metadata_ttl: int = metadata_ttl
        self.jwks_ttl: int = jwks_ttl

        self._metadata: EsiMetadataResponse = EsiMetadataResponse()
        self._metadata_expires_at: int = 0
        self._jwks_data: EsiJwksResponse | None = None
        self._jwks_expires_at: int = 0

    @property
    def _metadata_expired(self) -> bool:
        return int(time.time()) >= self._metadata_expires_at

    @property
    def _jwks_expired(self) -> bool:
        return int(time.time()) >= self._jwks_expires_at

    @property
    def _jwks(self) -> dict[str, EsiJwk] | None:
        if not self._jwks_data or self._jwks_expired:
            self.fetch_jwks()
        if not self._jwks_data:
            return None
        return {key.kid: key for key in self._jwks_data.keys if key.kid} or None

    @property
    def endpoints(self) -> EsiMetadataResponseEndpoints:
        return EsiMetadataResponseEndpoints.model_validate(self._metadata)

    @property
    def issuer(self) -> str:
        return EsiMetadataResponse.model_validate(self._metadata).issuer

    def discover_metadata(self, force: bool = False) -> EsiMetadataResponse:
        """Discover EVE SSO OAuth metadata."""
        if not force and not self._metadata_expired:
            return self._metadata

        res = self.api_client.call_api(method="GET", url=self.metadata_endpoints_url)
        self._metadata = EsiMetadataResponse.model_validate_json(res.read())
        self._metadata_expires_at = int(time.time()) + self.metadata_ttl
        return self._metadata

    def fetch_jwks(self, force: bool = False) -> EsiJwksResponse:
        """Fetch EVE SSO JWKs metadata."""
        if not force and self._jwks_data and not self._jwks_expired:
            return self._jwks_data

        metadata = self.discover_metadata()
        res = self.api_client.call_api(method="GET", url=metadata.jwks_uri)
        self._jwks_data = EsiJwksResponse.model_validate_json(res.read())
        self._jwks_expires_at = int(time.time()) + self.jwks_ttl
        return self._jwks_data

    def get_jwk(self, kid: str) -> EsiJwk | None:
        """Get JWK by key ID."""
        return self._jwks.get(kid) if self._jwks else None
