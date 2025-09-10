# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""Tests for the ContractsManager class."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from py_superops.exceptions import SuperOpsValidationError
from py_superops.graphql.types import (
    ContractRate,
    ContractSLA,
    ContractStatus,
    ContractType,
    SLALevel,
)
from py_superops.managers.contracts import ContractsManager


class TestContractsManager:
    """Test cases for ContractsManager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SuperOps client."""
        client = Mock()
        client.execute_query = AsyncMock()
        client.execute_mutation = AsyncMock()
        return client

    @pytest.fixture
    def contracts_manager(self, mock_client):
        """Create a ContractsManager instance with mocked client."""
        return ContractsManager(mock_client)

    @pytest.fixture
    def sample_contract_data(self):
        """Sample contract data for tests."""
        return {
            "id": "contract_123",
            "clientId": "client_456",
            "name": "Annual IT Support Contract",
            "contractNumber": "ITSupport-2024-001",
            "contractType": "SERVICE_AGREEMENT",
            "status": "ACTIVE",
            "startDate": "2024-01-01T00:00:00Z",
            "endDate": "2024-12-31T23:59:59Z",
            "renewalDate": None,
            "autoRenew": True,
            "billingCycle": "MONTHLY",
            "contractValue": 12000.00,
            "currency": "USD",
            "description": "Comprehensive IT support services",
            "termsAndConditions": "Standard terms apply",
            "renewalTerms": "Auto-renewal with 30-day notice",
            "cancellationTerms": "90-day cancellation notice required",
            "signedByClient": "John Smith",
            "signedByProvider": "Jane Doe",
            "signedDate": "2023-12-15T10:30:00Z",
            "notificationDays": 30,
            "tags": ["managed-services", "priority"],
            "customFields": {"account_manager": "Alice Johnson"},
            "createdAt": "2023-11-01T09:00:00Z",
            "updatedAt": "2023-12-15T10:30:00Z",
        }

    @pytest.fixture
    def sample_sla_data(self):
        """Sample SLA data for tests."""
        return {
            "id": "sla_789",
            "contractId": "contract_123",
            "level": "PREMIUM",
            "responseTimeMinutes": 15,
            "resolutionTimeHours": 4,
            "availabilityPercentage": 99.9,
            "description": "Premium support level with rapid response",
            "penalties": "Service credits for missed SLAs",
            "createdAt": "2023-11-01T09:00:00Z",
            "updatedAt": "2023-11-01T09:00:00Z",
        }

    @pytest.fixture
    def sample_rate_data(self):
        """Sample rate data for tests."""
        return {
            "id": "rate_101",
            "contractId": "contract_123",
            "serviceType": "Remote Support",
            "rateType": "HOURLY",
            "rateAmount": 150.00,
            "currency": "USD",
            "description": "Remote technical support hourly rate",
            "effectiveDate": "2024-01-01T00:00:00Z",
            "endDate": None,
            "createdAt": "2023-11-01T09:00:00Z",
            "updatedAt": "2023-11-01T09:00:00Z",
        }

    async def test_get_by_contract_number_success(
        self, contracts_manager, mock_client, sample_contract_data
    ):
        """Test successful contract retrieval by contract number."""
        # Mock the search response
        mock_client.execute_query.return_value = {
            "data": {
                "searchContracts": {
                    "items": [sample_contract_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 1,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_by_contract_number("ITSupport-2024-001")

        assert result is not None
        assert result.name == "Annual IT Support Contract"
        assert result.contract_number == "ITSupport-2024-001"
        mock_client.execute_query.assert_called_once()

    async def test_get_by_contract_number_not_found(self, contracts_manager, mock_client):
        """Test contract not found by contract number."""
        # Mock empty search response
        mock_client.execute_query.return_value = {
            "data": {
                "searchContracts": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "pageSize": 1,
                        "total": 0,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_by_contract_number("NONEXISTENT")

        assert result is None
        mock_client.execute_query.assert_called_once()

    async def test_get_by_contract_number_invalid_input(self, contracts_manager):
        """Test contract retrieval with invalid contract number."""
        with pytest.raises(
            SuperOpsValidationError, match="Contract number must be a non-empty string"
        ):
            await contracts_manager.get_by_contract_number("")

        with pytest.raises(
            SuperOpsValidationError, match="Contract number must be a non-empty string"
        ):
            await contracts_manager.get_by_contract_number(None)

    async def test_get_active_contracts(self, contracts_manager, mock_client, sample_contract_data):
        """Test retrieving active contracts."""
        mock_client.execute_query.return_value = {
            "data": {
                "contracts": {
                    "items": [sample_contract_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_active_contracts()

        assert len(result["items"]) == 1
        assert result["items"][0].status == ContractStatus.ACTIVE
        mock_client.execute_query.assert_called_once()

        # Check that the filter was applied correctly
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "ACTIVE"

    async def test_get_active_contracts_with_client_filter(
        self, contracts_manager, mock_client, sample_contract_data
    ):
        """Test retrieving active contracts filtered by client."""
        mock_client.execute_query.return_value = {
            "data": {
                "contracts": {
                    "items": [sample_contract_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_active_contracts(client_id="client_456")

        assert len(result["items"]) == 1
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "ACTIVE"
        assert variables["filters"]["clientId"] == "client_456"

    async def test_get_expiring_contracts(
        self, contracts_manager, mock_client, sample_contract_data
    ):
        """Test retrieving expiring contracts."""
        # Modify sample data to have an expiring end date
        expiring_data = sample_contract_data.copy()
        future_date = datetime.now() + timedelta(days=15)
        expiring_data["endDate"] = future_date.isoformat()

        mock_client.execute_query.return_value = {
            "data": {
                "contracts": {
                    "items": [expiring_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_expiring_contracts(days_threshold=30)

        assert len(result["items"]) == 1
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "ACTIVE"
        assert "endDateBefore" in variables["filters"]
        assert variables["sortBy"] == "endDate"
        assert variables["sortOrder"] == "ASC"

    async def test_get_expiring_contracts_invalid_threshold(self, contracts_manager):
        """Test expiring contracts with invalid threshold."""
        with pytest.raises(SuperOpsValidationError, match="Days threshold must be >= 1"):
            await contracts_manager.get_expiring_contracts(days_threshold=0)

    async def test_get_renewal_pending_contracts(
        self, contracts_manager, mock_client, sample_contract_data
    ):
        """Test retrieving contracts with renewal pending status."""
        renewal_pending_data = sample_contract_data.copy()
        renewal_pending_data["status"] = "RENEWAL_PENDING"
        renewal_pending_data["renewalDate"] = "2024-11-01T00:00:00Z"

        mock_client.execute_query.return_value = {
            "data": {
                "contracts": {
                    "items": [renewal_pending_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_renewal_pending_contracts()

        assert len(result["items"]) == 1
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["status"] == "RENEWAL_PENDING"
        assert variables["sortBy"] == "renewalDate"

    async def test_get_contracts_by_type(
        self, contracts_manager, mock_client, sample_contract_data
    ):
        """Test retrieving contracts by type."""
        mock_client.execute_query.return_value = {
            "data": {
                "contracts": {
                    "items": [sample_contract_data],
                    "pagination": {
                        "page": 1,
                        "pageSize": 50,
                        "total": 1,
                        "hasNextPage": False,
                        "hasPreviousPage": False,
                    },
                }
            }
        }

        result = await contracts_manager.get_contracts_by_type(ContractType.SERVICE_AGREEMENT)

        assert len(result["items"]) == 1
        call_args = mock_client.execute_query.call_args
        variables = call_args[0][1]
        assert variables["filters"]["contractType"] == "SERVICE_AGREEMENT"

    async def test_get_contracts_by_type_invalid_type(self, contracts_manager):
        """Test contracts by type with invalid type."""
        with pytest.raises(
            SuperOpsValidationError, match="Contract type must be a ContractType enum"
        ):
            await contracts_manager.get_contracts_by_type("INVALID_TYPE")

    async def test_activate_contract(self, contracts_manager, mock_client, sample_contract_data):
        """Test activating a contract."""
        active_data = sample_contract_data.copy()
        active_data["status"] = "ACTIVE"

        mock_client.execute_mutation.return_value = {"data": {"updateContract": active_data}}

        result = await contracts_manager.activate_contract("contract_123")

        assert result.status == ContractStatus.ACTIVE
        mock_client.execute_mutation.assert_called_once()

    async def test_activate_contract_invalid_id(self, contracts_manager):
        """Test activating contract with invalid ID."""
        with pytest.raises(SuperOpsValidationError, match="Invalid contract ID"):
            await contracts_manager.activate_contract("")

    async def test_suspend_contract(self, contracts_manager, mock_client, sample_contract_data):
        """Test suspending a contract."""
        suspended_data = sample_contract_data.copy()
        suspended_data["status"] = "SUSPENDED"

        mock_client.execute_mutation.return_value = {"data": {"updateContract": suspended_data}}

        result = await contracts_manager.suspend_contract("contract_123")

        assert result.status == ContractStatus.SUSPENDED
        mock_client.execute_mutation.assert_called_once()

    async def test_cancel_contract(self, contracts_manager, mock_client, sample_contract_data):
        """Test cancelling a contract."""
        cancelled_data = sample_contract_data.copy()
        cancelled_data["status"] = "CANCELLED"

        mock_client.execute_mutation.return_value = {"data": {"updateContract": cancelled_data}}

        result = await contracts_manager.cancel_contract("contract_123", "Customer request")

        assert result.status == ContractStatus.CANCELLED
        mock_client.execute_mutation.assert_called_once()

        # Check that cancellation reason was included
        call_args = mock_client.execute_mutation.call_args
        variables = call_args[0][1]
        assert variables["input"]["cancellationReason"] == "Customer request"

    async def test_renew_contract(self, contracts_manager, mock_client, sample_contract_data):
        """Test renewing a contract."""
        renewed_data = sample_contract_data.copy()
        new_end_date = datetime.now() + timedelta(days=365)
        renewed_data["endDate"] = new_end_date.isoformat()
        renewed_data["contractValue"] = 15000.00
        renewed_data["renewalDate"] = None

        mock_client.execute_mutation.return_value = {"data": {"updateContract": renewed_data}}

        result = await contracts_manager.renew_contract("contract_123", new_end_date, 15000.00)

        assert result.status == ContractStatus.ACTIVE
        assert result.contract_value == 15000.00
        mock_client.execute_mutation.assert_called_once()

    async def test_renew_contract_invalid_date(self, contracts_manager):
        """Test renewing contract with invalid date."""
        past_date = datetime.now() - timedelta(days=1)

        with pytest.raises(SuperOpsValidationError, match="New end date must be in the future"):
            await contracts_manager.renew_contract("contract_123", past_date)

        with pytest.raises(SuperOpsValidationError, match="New end date must be a datetime object"):
            await contracts_manager.renew_contract("contract_123", "2024-12-31")

    async def test_set_renewal_pending(self, contracts_manager, mock_client, sample_contract_data):
        """Test setting contract to renewal pending."""
        renewal_pending_data = sample_contract_data.copy()
        renewal_date = datetime.now() + timedelta(days=60)
        renewal_pending_data["status"] = "RENEWAL_PENDING"
        renewal_pending_data["renewalDate"] = renewal_date.isoformat()

        mock_client.execute_mutation.return_value = {
            "data": {"updateContract": renewal_pending_data}
        }

        result = await contracts_manager.set_renewal_pending("contract_123", renewal_date)

        assert result.status == ContractStatus.RENEWAL_PENDING
        mock_client.execute_mutation.assert_called_once()

    async def test_add_sla(self, contracts_manager, mock_client, sample_sla_data):
        """Test adding SLA to a contract."""
        mock_client.execute_mutation.return_value = {"data": {"createContractSLA": sample_sla_data}}

        sla_input = {
            "level": "PREMIUM",
            "responseTimeMinutes": 15,
            "resolutionTimeHours": 4,
            "availabilityPercentage": 99.9,
            "description": "Premium support level",
            "penalties": "Service credits for missed SLAs",
        }

        result = await contracts_manager.add_sla("contract_123", sla_input)

        assert isinstance(result, ContractSLA)
        assert result.level == SLALevel.PREMIUM
        assert result.response_time_minutes == 15
        mock_client.execute_mutation.assert_called_once()

    async def test_add_sla_invalid_input(self, contracts_manager):
        """Test adding SLA with invalid input."""
        with pytest.raises(SuperOpsValidationError, match="Invalid contract ID"):
            await contracts_manager.add_sla("", {})

        with pytest.raises(SuperOpsValidationError, match="SLA data cannot be empty"):
            await contracts_manager.add_sla("contract_123", {})

    async def test_add_rate(self, contracts_manager, mock_client, sample_rate_data):
        """Test adding rate to a contract."""
        mock_client.execute_mutation.return_value = {
            "data": {"createContractRate": sample_rate_data}
        }

        rate_input = {
            "serviceType": "Remote Support",
            "rateType": "HOURLY",
            "rateAmount": 150.00,
            "currency": "USD",
            "description": "Remote technical support hourly rate",
        }

        result = await contracts_manager.add_rate("contract_123", rate_input)

        assert isinstance(result, ContractRate)
        assert result.service_type == "Remote Support"
        assert result.rate_amount == 150.00
        mock_client.execute_mutation.assert_called_once()

    async def test_add_rate_invalid_input(self, contracts_manager):
        """Test adding rate with invalid input."""
        with pytest.raises(SuperOpsValidationError, match="Invalid contract ID"):
            await contracts_manager.add_rate("", {})

        with pytest.raises(SuperOpsValidationError, match="Rate data cannot be empty"):
            await contracts_manager.add_rate("contract_123", {})

    async def test_bulk_update_status(self, contracts_manager, mock_client, sample_contract_data):
        """Test bulk status update for multiple contracts."""
        updated_data_1 = sample_contract_data.copy()
        updated_data_1["id"] = "contract_123"
        updated_data_1["status"] = "SUSPENDED"

        updated_data_2 = sample_contract_data.copy()
        updated_data_2["id"] = "contract_456"
        updated_data_2["status"] = "SUSPENDED"

        # Mock multiple update calls
        mock_client.execute_mutation.side_effect = [
            {"data": {"updateContract": updated_data_1}},
            {"data": {"updateContract": updated_data_2}},
        ]

        result = await contracts_manager.bulk_update_status(
            ["contract_123", "contract_456"], ContractStatus.SUSPENDED
        )

        assert len(result) == 2
        assert all(contract.status == ContractStatus.SUSPENDED for contract in result)
        assert mock_client.execute_mutation.call_count == 2

    async def test_bulk_update_status_invalid_input(self, contracts_manager):
        """Test bulk status update with invalid input."""
        with pytest.raises(SuperOpsValidationError, match="Contract IDs list cannot be empty"):
            await contracts_manager.bulk_update_status([], ContractStatus.ACTIVE)

        with pytest.raises(SuperOpsValidationError, match="Contract IDs must be a list"):
            await contracts_manager.bulk_update_status("not_a_list", ContractStatus.ACTIVE)

        with pytest.raises(SuperOpsValidationError, match="Status must be a ContractStatus enum"):
            await contracts_manager.bulk_update_status(["contract_123"], "INVALID_STATUS")

    async def test_validate_create_data(self, contracts_manager):
        """Test contract creation data validation."""
        # Test valid data
        valid_data = {
            "clientId": "client_123",
            "name": "Test Contract",
            "contractType": "SERVICE_AGREEMENT",
            "startDate": "2024-01-01T00:00:00Z",
        }

        result = contracts_manager._validate_create_data(valid_data)
        assert result["clientId"] == "client_123"

        # Test missing required fields
        with pytest.raises(SuperOpsValidationError, match="Client ID is required"):
            contracts_manager._validate_create_data({})

        with pytest.raises(SuperOpsValidationError, match="Contract name is required"):
            contracts_manager._validate_create_data({"clientId": "client_123"})

        # Test invalid contract type
        invalid_type_data = {
            "clientId": "client_123",
            "name": "Test Contract",
            "contractType": "INVALID_TYPE",
            "startDate": "2024-01-01T00:00:00Z",
        }
        with pytest.raises(SuperOpsValidationError, match="Invalid contract type"):
            contracts_manager._validate_create_data(invalid_type_data)

        # Test invalid contract value
        invalid_value_data = {
            "clientId": "client_123",
            "name": "Test Contract",
            "contractType": "SERVICE_AGREEMENT",
            "startDate": "2024-01-01T00:00:00Z",
            "contractValue": -1000,
        }
        with pytest.raises(SuperOpsValidationError, match="Contract value must be >= 0"):
            contracts_manager._validate_create_data(invalid_value_data)

    async def test_validate_sla_data(self, contracts_manager):
        """Test SLA data validation."""
        # Test valid SLA data
        valid_sla = {
            "level": "PREMIUM",
            "responseTimeMinutes": 15,
            "resolutionTimeHours": 4,
            "availabilityPercentage": 99.9,
        }

        result = contracts_manager._validate_sla_data(valid_sla)
        assert result["level"] == "PREMIUM"

        # Test missing required fields
        with pytest.raises(SuperOpsValidationError, match="SLA level is required"):
            contracts_manager._validate_sla_data({})

        # Test invalid SLA level
        with pytest.raises(SuperOpsValidationError, match="Invalid SLA level"):
            contracts_manager._validate_sla_data({"level": "INVALID_LEVEL"})

        # Test invalid time values
        with pytest.raises(SuperOpsValidationError, match="Response time must be >= 0"):
            contracts_manager._validate_sla_data({"level": "PREMIUM", "responseTimeMinutes": -5})

        with pytest.raises(
            SuperOpsValidationError, match="Availability percentage must be between 0 and 100"
        ):
            contracts_manager._validate_sla_data(
                {"level": "PREMIUM", "availabilityPercentage": 150}
            )

    async def test_validate_rate_data(self, contracts_manager):
        """Test rate data validation."""
        # Test valid rate data
        valid_rate = {"serviceType": "Remote Support", "rateType": "HOURLY", "rateAmount": 150.00}

        result = contracts_manager._validate_rate_data(valid_rate)
        assert result["serviceType"] == "Remote Support"

        # Test missing required fields
        with pytest.raises(SuperOpsValidationError, match="Service type is required"):
            contracts_manager._validate_rate_data({"rateAmount": 150})

        with pytest.raises(SuperOpsValidationError, match="Rate type is required"):
            contracts_manager._validate_rate_data({"serviceType": "Support", "rateAmount": 150})

        with pytest.raises(SuperOpsValidationError, match="Rate amount is required"):
            contracts_manager._validate_rate_data({"serviceType": "Support", "rateType": "HOURLY"})

        # Test invalid rate amount
        with pytest.raises(SuperOpsValidationError, match="Rate amount must be >= 0"):
            contracts_manager._validate_rate_data(
                {"serviceType": "Support", "rateType": "HOURLY", "rateAmount": -50}
            )

    async def test_get_with_slas(self, contracts_manager, mock_client, sample_contract_data):
        """Test getting contract with SLAs."""
        contract_with_slas = sample_contract_data.copy()
        contract_with_slas["slas"] = [
            {"id": "sla_1", "level": "PREMIUM", "responseTimeMinutes": 15}
        ]

        mock_client.execute_query.return_value = {"data": {"contract": contract_with_slas}}

        result = await contracts_manager.get_with_slas("contract_123")

        assert result is not None
        assert len(result.slas) == 1
        mock_client.execute_query.assert_called_once()

        # Verify include_slas was passed
        call_args = mock_client.execute_query.call_args
        assert "include_slas" in call_args[1]
        assert call_args[1]["include_slas"] is True

    async def test_get_with_rates(self, contracts_manager, mock_client, sample_contract_data):
        """Test getting contract with rates."""
        contract_with_rates = sample_contract_data.copy()
        contract_with_rates["rates"] = [
            {"id": "rate_1", "serviceType": "Support", "rateAmount": 150.00}
        ]

        mock_client.execute_query.return_value = {"data": {"contract": contract_with_rates}}

        result = await contracts_manager.get_with_rates("contract_123")

        assert result is not None
        assert len(result.rates) == 1
        mock_client.execute_query.assert_called_once()

        # Verify include_rates was passed
        call_args = mock_client.execute_query.call_args
        assert "include_rates" in call_args[1]
        assert call_args[1]["include_rates"] is True

    async def test_build_graphql_queries(self, contracts_manager):
        """Test GraphQL query building methods."""
        # Test get query
        get_query = contracts_manager._build_get_query()
        assert "query GetContract($id: ID!)" in get_query
        assert "contract(id: $id)" in get_query

        # Test get query with includes
        get_query_with_slas = contracts_manager._build_get_query(include_slas=True)
        assert "slas {" in get_query_with_slas

        get_query_with_rates = contracts_manager._build_get_query(include_rates=True)
        assert "rates {" in get_query_with_rates

        # Test list query
        list_query = contracts_manager._build_list_query()
        assert "query ListContracts(" in list_query
        assert "contracts(" in list_query

        # Test create mutation
        create_mutation = contracts_manager._build_create_mutation()
        assert "mutation CreateContract($input: CreateContractInput!)" in create_mutation

        # Test update mutation
        update_mutation = contracts_manager._build_update_mutation()
        assert "mutation UpdateContract($id: ID!, $input: UpdateContractInput!)" in update_mutation

        # Test delete mutation
        delete_mutation = contracts_manager._build_delete_mutation()
        assert "mutation DeleteContract($id: ID!)" in delete_mutation

        # Test search query
        search_query = contracts_manager._build_search_query()
        assert "query SearchContracts(" in search_query

        # Test SLA mutations
        sla_mutation = contracts_manager._build_create_sla_mutation()
        assert "mutation CreateContractSLA($input: CreateContractSLAInput!)" in sla_mutation

        rate_mutation = contracts_manager._build_create_rate_mutation()
        assert "mutation CreateContractRate($input: CreateContractRateInput!)" in rate_mutation
