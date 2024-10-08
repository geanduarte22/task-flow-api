from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
import pytest
from unittest.mock import patch
from api.auth import get_api_key
from core.config import settings


@pytest.mark.asyncio
async def test_get_api_key_valid():
    with patch("core.config.settings.API_KEY", "valid-api-key"):
        result = await get_api_key("valid-api-key")
        assert result == "valid-api-key"


@pytest.mark.asyncio
async def test_get_api_key_invalid():
    with patch("core.config.settings.API_KEY", "valid-api-key"):
        with pytest.raises(HTTPException) as excinfo:
            await get_api_key("invalid-api-key")

        assert excinfo.value.status_code == HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Invalid or missing API Key"


@pytest.mark.asyncio
async def test_get_api_key_missing():
    with patch("core.config.settings.API_KEY", "valid-api-key"):
        with pytest.raises(HTTPException) as excinfo:
            await get_api_key(None)

        assert excinfo.value.status_code == HTTP_401_UNAUTHORIZED
        assert excinfo.value.detail == "Invalid or missing API Key"
