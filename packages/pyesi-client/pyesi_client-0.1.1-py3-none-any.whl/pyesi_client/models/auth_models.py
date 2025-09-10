"""Authentication-related models."""

import base64
from typing import Any

from pydantic import BaseModel, ConfigDict, model_serializer

from pyesi_client.constants import (
    EsiCodeChallengeMethod,
    EsiGrantType,
    EsiResponseType,
)


class EsiAuthorizationUrlParams(BaseModel):
    """OAuth authorization URL parameters."""

    model_config = ConfigDict(use_enum_values=True)

    response_type: EsiResponseType = EsiResponseType.CODE
    redirect_uri: str
    client_id: str
    scope: str = ""
    state: str
    code_challenge: str | None = None
    code_challenge_method: EsiCodeChallengeMethod | None = None


class EsiAuthorizationUrlData(BaseModel):
    """Authorization URL with state parameter."""

    url: str
    state: str


class EsiPKCEResult(BaseModel):
    """PKCE verifier and challenge pair."""

    verifier: str
    challenge: str


class EsiTokenPKCE(BaseModel):
    """PKCE data for token requests."""

    client_id: str
    code_verifier: str


class EsiBasicAuthHeaders(BaseModel):
    """Basic auth header data."""

    client_id: str
    client_secret: str
    encoding: str = "utf-8"


class EsiRequestHeaders(BaseModel):
    """HTTP request headers for OAuth."""

    content_type: str = "application/x-www-form-urlencoded"
    basic_auth_headers: EsiBasicAuthHeaders | None = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        data = {"Content-Type": self.content_type}
        if self.basic_auth_headers is not None:
            basic_auth = base64.urlsafe_b64encode(
                f"{self.basic_auth_headers.client_id}:{self.basic_auth_headers.client_secret}".encode(
                    self.basic_auth_headers.encoding
                )
            ).decode()
            data["Authorization"] = f"Basic {basic_auth}"
        return data


class EsiTokenRequest(BaseModel):
    """Base token request model."""

    model_config = ConfigDict(use_enum_values=True)

    grant_type: EsiGrantType
    pkce: EsiTokenPKCE | None = None

    @model_serializer
    def ser_model(self) -> dict[str, Any]:
        data = {"grant_type": self.grant_type.value}
        for field_name in self.__class__.model_fields:
            if field_name not in {"grant_type", "pkce"}:
                field_value = getattr(self, field_name)
                if field_value is not None:
                    data[field_name] = field_value
        if self.pkce is not None:
            data["client_id"] = self.pkce.client_id
            data["code_verifier"] = self.pkce.code_verifier
        return data


class EsiAuthorizationCodeRequest(EsiTokenRequest):
    """Authorization code token request."""

    grant_type: EsiGrantType = EsiGrantType.AUTHORIZATION_CODE
    code: str


class EsiRefreshTokenRequest(EsiTokenRequest):
    """Refresh token request."""

    grant_type: EsiGrantType = EsiGrantType.REFRESH_TOKEN
    refresh_token: str
