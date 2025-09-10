"""JWK (JSON Web Key) related models."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator

from pyesi_client.constants import (
    DEFAULT_ESI_AUTH_ENDPOINT,
    DEFAULT_ESI_ISSUER_ENDPOINT,
    DEFAULT_ESI_JWKS_URI,
    DEFAULT_ESI_REVOCATION_ENDPOINT,
    DEFAULT_ESI_TOKEN_ENDPOINT,
    EsiCodeChallengeMethod,
    EsiIdTokenSigningAlgValue,
    EsiResponseType,
    EsiRevocationEndpointAuthMethod,
    EsiSubjectType,
    EsiTokenEndpointAuthMethod,
    EsiTokenEndpointAuthSigningAlgValue,
)


class EsiMetadataResponseEndpoints(BaseModel):
    """OAuth metadata endpoints."""

    model_config = ConfigDict(extra="allow")

    authorization_endpoint: str = DEFAULT_ESI_AUTH_ENDPOINT
    token_endpoint: str = DEFAULT_ESI_TOKEN_ENDPOINT
    jwks_uri: str = DEFAULT_ESI_JWKS_URI
    revocation_endpoint: str = DEFAULT_ESI_REVOCATION_ENDPOINT


class EsiMetadataResponse(EsiMetadataResponseEndpoints):
    """Complete EVE SSO OAuth metadata response."""

    model_config = ConfigDict(extra="allow")

    issuer: str = DEFAULT_ESI_ISSUER_ENDPOINT
    response_types_supported: list[EsiResponseType | str] = list(EsiResponseType)
    subject_types_supported: list[EsiSubjectType | str] = list(EsiSubjectType)
    revocation_endpoint_auth_methods_supported: list[EsiRevocationEndpointAuthMethod | str] = list(
        EsiRevocationEndpointAuthMethod
    )
    token_endpoint_auth_methods_supported: list[EsiTokenEndpointAuthMethod | str] = list(EsiTokenEndpointAuthMethod)
    id_token_signing_alg_values_supported: list[EsiIdTokenSigningAlgValue | str] = list(EsiIdTokenSigningAlgValue)
    token_endpoint_auth_signing_alg_values_supported: list[EsiTokenEndpointAuthSigningAlgValue | str] = list(
        EsiTokenEndpointAuthSigningAlgValue
    )
    code_challenge_methods_supported: list[EsiCodeChallengeMethod | str] = list(EsiCodeChallengeMethod)


class EsiJwkRS256(BaseModel):
    """RSA JWK for RS256 signatures."""

    alg: Literal["RS256"]
    e: Literal["AQAB"]
    kid: str
    kty: Literal["RSA"]
    n: str
    use: Literal["sig"]


class EsiJwkES256(BaseModel):
    """EC JWK for ES256 signatures."""

    alg: Literal["ES256"]
    crv: Literal["P-256"]
    kid: str
    kty: Literal["EC"]
    use: Literal["sig"]
    x: str
    y: str


type EsiJwk = EsiJwkRS256 | EsiJwkES256


class EsiJwksResponse(BaseModel):
    """EVE SSO JWKS metadata response."""

    model_config = ConfigDict(extra="allow")
    keys: list[EsiJwk]
    skipUnresolvedJsonWebKeys: bool = True

    @field_validator("keys", mode="before")
    @classmethod
    def validate_keys(cls, v: Any) -> Any:
        """Validate and convert keys to appropriate JWK models."""
        if isinstance(v, list):
            validated_keys: list[EsiJwk] = []
            for key_metadata in v:
                if isinstance(key_metadata, (EsiJwkRS256, EsiJwkES256)):
                    validated_keys.append(key_metadata)
                elif isinstance(key_metadata, dict):
                    kty = key_metadata.get("kty")
                    alg = key_metadata.get("alg")
                    if kty == "EC" or alg == "ES256":
                        validated_keys.append(EsiJwkES256.model_validate(key_metadata))
                    else:
                        validated_keys.append(EsiJwkRS256.model_validate(key_metadata))
                else:
                    validated_keys.append(EsiJwkRS256.model_validate(key_metadata))
            return validated_keys
        return v
