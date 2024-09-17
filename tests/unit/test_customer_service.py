from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from schemas.customer import CustomerDTO, CustomerResponseDTO, CustomerUpdateDTO
from services.customer import CustomerService
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_customer(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    new_customer_mock = MagicMock()
    new_customer_mock.customer_key = "some-key"
    new_customer_mock.name = "John Doe"
    new_customer_mock.email = "john@example.com"
    new_customer_mock.status.enumerator = "active"
    new_customer_mock.created_at = datetime(2024, 1, 1, 0, 0, 0)
    new_customer_mock.updated_at = datetime(2024, 1, 1, 0, 0, 0)

    customer_repository.create.return_value = new_customer_mock

    service = CustomerService(session)
    service.customer_repository = customer_repository

    dto = CustomerDTO(name="John Doe", email="john@example.com")

    result = await service.create_customer(dto)

    # Verificações
    assert db_session is not None
    assert isinstance(result, CustomerResponseDTO)
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert result.status == "active"
    customer_repository.create.assert_called_once_with(
        name="John Doe", email="john@example.com"
    )


@pytest.mark.asyncio
async def test_get_customer(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    customer_mock = MagicMock()
    customer_mock.customer_key = "some-key"
    customer_mock.name = "John Doe"
    customer_mock.email = "john.doe@example.com"
    customer_mock.status.enumerator = "active"
    customer_mock.created_at = datetime(2024, 1, 1, 0, 0, 0)
    customer_mock.updated_at = datetime(2024, 1, 1, 0, 0, 0)

    customer_repository.get_by_key.return_value = customer_mock

    service = CustomerService(session)
    service.customer_repository = customer_repository

    result = await service.get_customer("some-key")

    assert db_session is not None
    assert isinstance(result, CustomerResponseDTO)
    assert result.customer_key == "some-key"
    assert result.name == "John Doe"
    assert result.email == "john.doe@example.com"
    assert result.status == "active"
    customer_repository.get_by_key.assert_called_once_with("some-key")


@pytest.mark.asyncio
async def test_update_customer(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    customer_mock = MagicMock()
    customer_mock.customer_key = "some-key"
    customer_mock.name = "John Doe"
    customer_mock.email = "john.doe@example.com"
    customer_mock.status.enumerator = "active"
    customer_mock.created_at = datetime(2024, 1, 1, 0, 0, 0)
    customer_mock.updated_at = datetime(2024, 1, 1, 0, 0, 0)

    customer_repository.get_by_key.return_value = customer_mock

    updated_customer_mock = MagicMock()
    updated_customer_mock.customer_key = "some-key"
    updated_customer_mock.name = "Jane Doe"
    updated_customer_mock.email = "jane.doe@example.com"
    updated_customer_mock.status.enumerator = "active"
    updated_customer_mock.created_at = datetime(2024, 1, 1, 0, 0, 0)
    updated_customer_mock.updated_at = datetime(2024, 1, 2, 0, 0, 0)

    customer_repository.update.return_value = updated_customer_mock

    service = CustomerService(session)
    service.customer_repository = customer_repository

    dto = CustomerUpdateDTO(
        name="Jane Doe", email="jane.doe@example.com", status="active"
    )

    result = await service.update_customer("some-key", dto)

    assert db_session is not None
    assert isinstance(result, CustomerResponseDTO)
    assert result.name == "Jane Doe" 
    assert result.email == "jane.doe@example.com"
    assert result.status == "active"
    assert result.updated_at == datetime(2024, 1, 2, 0, 0, 0)

    customer_repository.get_by_key.assert_called_once_with("some-key")
    customer_repository.update.assert_called_once_with(
        customer_mock, "Jane Doe", "jane.doe@example.com", "active"
    )


@pytest.mark.asyncio
async def test_get_customer_not_found(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    # Simular que o cliente não foi encontrado
    customer_repository.get_by_key.return_value = None

    service = CustomerService(session)
    service.customer_repository = customer_repository

    # Verificar se uma exceção HTTP 404 é levantada
    with pytest.raises(HTTPException) as excinfo:
        await service.get_customer("nonexistent-customer-key")

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Customer not found"
    customer_repository.get_by_key.assert_called_once_with("nonexistent-customer-key")


@pytest.mark.asyncio
async def test_create_customer_internal_error(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    # Simular uma exceção ao criar o cliente
    customer_repository.create.side_effect = Exception("Database error")

    service = CustomerService(session)
    service.customer_repository = customer_repository

    dto = CustomerDTO(name="John Doe", email="john@example.com")

    # Verificar se uma exceção HTTP 500 é levantada
    with pytest.raises(HTTPException) as excinfo:
        await service.create_customer(dto)

    assert excinfo.value.status_code == 500
    assert "internal error" in str(excinfo.value.detail).lower()
    customer_repository.create.assert_called_once_with(
        name="John Doe", email="john@example.com"
    )

@pytest.mark.asyncio
async def test_update_customer_not_found(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    # Simular que o cliente não foi encontrado
    customer_repository.get_by_key.return_value = None

    service = CustomerService(session)
    service.customer_repository = customer_repository

    dto = CustomerUpdateDTO(name="Jane Doe", email="jane.doe@example.com", status="active")

    # Verificar se uma exceção HTTP 404 é levantada
    with pytest.raises(HTTPException) as excinfo:
        await service.update_customer("nonexistent-customer-key", dto)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Customer not found"
    customer_repository.get_by_key.assert_called_once_with("nonexistent-customer-key")


@pytest.mark.asyncio
async def test_update_customer_internal_error(db_session):
    session = MagicMock()
    customer_repository = AsyncMock()

    customer_mock = MagicMock()
    customer_repository.get_by_key.return_value = customer_mock

    # Simular uma exceção ao atualizar o cliente
    customer_repository.update.side_effect = Exception("Database error")

    service = CustomerService(session)
    service.customer_repository = customer_repository

    dto = CustomerUpdateDTO(name="Jane Doe", email="jane.doe@example.com", status="active")

    # Verificar se uma exceção HTTP 500 é levantada
    with pytest.raises(HTTPException) as excinfo:
        await service.update_customer("some-key", dto)

    assert excinfo.value.status_code == 500
    assert "internal error" in str(excinfo.value.detail).lower()
    customer_repository.get_by_key.assert_called_once_with("some-key")
    customer_repository.update.assert_called_once_with(
        customer_mock, "Jane Doe", "jane.doe@example.com", "active"
    )
