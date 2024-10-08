import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app import on_startup, on_shutdown, create, handle_input_output
from fastapi import Request
from fastapi.testclient import TestClient
from core.config import settings


@pytest.mark.asyncio
async def test_on_startup():
    """Teste unitário para a função on_startup."""
    with patch("app.MySQLConnector.create_engine") as mock_create_engine:
        await on_startup()
        mock_create_engine.assert_called_once()


@pytest.mark.asyncio
async def test_on_shutdown():
    """Teste unitário para a função on_shutdown."""
    with patch("app.MySQLConnector.dispose_engine") as mock_dispose_engine:
        await on_shutdown()
        mock_dispose_engine.assert_called_once()


def test_create_app():
    """Teste unitário para a função create que configura o app FastAPI."""
    app_instance = create()
    assert app_instance.title == settings.SERVICE_NAME
    assert app_instance.version == "1.0.0"

    routes = [route.path for route in app_instance.routes]

    assert (
        f"{settings.API_V1_STR}/openapi.json" in routes
    ), f"OpenAPI route not found in {routes}"

    assert len(routes) > 1, "Nenhuma rota de API registrada além da documentação"


@pytest.mark.asyncio
async def test_handle_input_output():
    """Teste unitário para o middleware handle_input_output."""
    request = MagicMock(spec=Request)
    request.url.path = "/favicon.ico"

    call_next = AsyncMock()

    response = await handle_input_output(request, call_next)
    call_next.assert_called_once_with(request)

    request.url.path = "/api/v1/resource"
    call_next.reset_mock()
    response = await handle_input_output(request, call_next)
    call_next.assert_called_once_with(request)
