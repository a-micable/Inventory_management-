"""API version management."""

from __future__ import annotations

from enum import Enum


class APIVersion(str, Enum):
    V1 = "v1"

    @property
    def prefix(self) -> str:
        return f"/api/{self.value}"


CURRENT_VERSION = APIVersion.V1
SUPPORTED_VERSIONS = [APIVersion.V1]
