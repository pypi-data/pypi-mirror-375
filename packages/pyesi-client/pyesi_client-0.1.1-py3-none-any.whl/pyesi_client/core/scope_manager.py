"""
pyesi-client:

ESI Scope Manager
"""

from typing import Self

from pydantic import BaseModel, Field, field_validator

from pyesi_client.constants import EsiScope


class EsiScopeManager(BaseModel):
    """Manager for type-safe EVE SSO OAuth scopes."""

    scopes: set[EsiScope] = Field(default_factory=set)

    @field_validator("scopes", mode="before")
    @classmethod
    def validate_scopes(cls, value: set[EsiScope] | list[EsiScope | str]) -> set[EsiScope]:
        """Convert input to EsiScope set."""
        if isinstance(value, set):
            return value
        return {EsiScope(scope) if isinstance(scope, str) else scope for scope in value}

    def add(self, *scopes: EsiScope) -> Self:
        """Add one or more scopes."""
        self.scopes.update(scopes)
        return self

    def add_from_list(self, scopes: list[EsiScope]) -> Self:
        """Add a list of scopes."""
        self.scopes.update(scopes)
        return self

    def remove(self, scope: EsiScope) -> Self:
        """Remove a scope."""
        self.scopes.discard(scope)
        return self

    def has(self, scope: EsiScope) -> bool:
        """Check if scope exists."""
        return scope in self.scopes

    def to_oauth_string(self) -> str:
        """Convert to OAuth string."""
        return " ".join(sorted(scope.value for scope in self.scopes))

    def matches(self, jwt_scopes: list[str] | str | set[EsiScope]) -> bool:
        """Check if scopes match JWT scopes."""
        if isinstance(jwt_scopes, str):
            jwt_scopes = jwt_scopes.split()
        elif isinstance(jwt_scopes, set):
            jwt_scopes = [scope.value for scope in jwt_scopes]

        return {scope.value for scope in self.scopes} == set(jwt_scopes)
