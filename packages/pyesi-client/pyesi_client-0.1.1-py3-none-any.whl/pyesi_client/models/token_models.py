"""Token-related models."""

import time
from typing import Any, Literal, Self

from pydantic import BaseModel, computed_field, field_validator

from pyesi_client.constants import EsiScope


class EsiTokenResponse(BaseModel):
    """OAuth token response."""

    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int
    refresh_token: str


class EsiTokenSet(BaseModel):
    """Token set with expiration tracking."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_at: int

    @classmethod
    def from_token_response(cls, token_response: EsiTokenResponse) -> Self:
        """Create TokenSet from token response."""
        now = int(time.time())
        expires_at = now + token_response.expires_in
        return cls(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            token_type=token_response.token_type,
            expires_at=expires_at,
        )


class EsiJwtTokenData(BaseModel):
    """Verified JWT token data from EVE SSO."""

    scp: list[EsiScope]  # scopes
    jti: str  # JWT ID
    kid: str  # key ID
    sub: str  # subject (CHARACTER:EVE:{character_id})
    azp: str  # authorized party (client ID)
    tenant: str  # EVE server (tranquility/singularity)
    tier: str  # live/test
    region: str  # world region
    aud: list[str]  # audience
    name: str  # character name
    owner: str  # owner hash
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    iss: str  # issuer

    @computed_field
    @property
    def character_id(self) -> int:
        """Extract character ID from sub field."""
        if self.sub.startswith("CHARACTER:EVE:"):
            return int(self.sub.split(":")[2])
        raise ValueError(f"Invalid sub format: {self.sub}")

    @computed_field
    @property
    def character_name(self) -> str:
        return self.name

    @field_validator("scp", mode="before")
    @classmethod
    def validate_scopes(cls, v: Any) -> list[EsiScope]:
        """Convert scope strings to EsiScope enum values."""
        if isinstance(v, list):
            scopes = []
            for scope in v:
                if isinstance(scope, str):
                    for esi_scope in EsiScope:
                        if esi_scope.value == scope:
                            scopes.append(esi_scope)
                            break
                    else:
                        scopes.append(scope)
                else:
                    scopes.append(scope)
            return scopes
        return v
