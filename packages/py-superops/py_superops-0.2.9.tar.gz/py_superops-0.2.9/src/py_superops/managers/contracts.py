# Copyright (c) 2025 Aaron Sachs
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.


"""Contract manager for SuperOps API operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..exceptions import SuperOpsValidationError
from ..graphql.types import (
    BillingCycle,
    Contract,
    ContractRate,
    ContractSLA,
    ContractStatus,
    ContractType,
    SLALevel,
)
from .base import ResourceManager


class ContractsManager(ResourceManager[Contract]):
    """Manager for contract operations.

    Provides high-level methods for managing SuperOps contracts including
    CRUD operations, business logic, and contract-specific workflows.
    """

    def __init__(self, client):
        """Initialize the contracts manager.

        Args:
            client: SuperOps client instance
        """
        super().__init__(client, Contract, "contract")

    async def get_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """Get a contract by contract number.

        Args:
            contract_number: Contract number to search for

        Returns:
            Contract instance or None if not found

        Raises:
            SuperOpsValidationError: If contract_number is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contract_number or not isinstance(contract_number, str):
            raise SuperOpsValidationError("Contract number must be a non-empty string")

        self.logger.debug(f"Getting contract by number: {contract_number}")

        # Use search with exact contract number match
        results = await self.search(f'contractNumber:"{contract_number}"', page_size=1)

        # Return first exact match if any
        for contract in results["items"]:
            if contract.contract_number == contract_number:
                return contract

        return None

    async def get_with_slas(self, contract_id: str) -> Optional[Contract]:
        """Get a contract with all associated SLAs loaded.

        Args:
            contract_id: The contract ID

        Returns:
            Contract instance with SLAs or None if not found

        Raises:
            SuperOpsValidationError: If contract_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Getting contract with SLAs: {contract_id}")

        return await self.get(contract_id, include_slas=True)

    async def get_with_rates(self, contract_id: str) -> Optional[Contract]:
        """Get a contract with all associated rates loaded.

        Args:
            contract_id: The contract ID

        Returns:
            Contract instance with rates or None if not found

        Raises:
            SuperOpsValidationError: If contract_id is invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Getting contract with rates: {contract_id}")

        return await self.get(contract_id, include_rates=True)

    async def get_active_contracts(
        self,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Dict[str, Any]:
        """Get all active contracts.

        Args:
            client_id: Optional client ID to filter by
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by (default: name)
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            Dictionary containing 'items' (List[Contract]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug(f"Getting active contracts - page: {page}, size: {page_size}")

        filters = {"status": ContractStatus.ACTIVE.value}
        if client_id:
            filters["clientId"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by=sort_by or "name",
            sort_order=sort_order,
        )

    async def get_expiring_contracts(
        self,
        days_threshold: int = 30,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get contracts expiring within a specified number of days.

        Args:
            days_threshold: Number of days to look ahead for expiring contracts
            client_id: Optional client ID to filter by
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[Contract]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if days_threshold < 1:
            raise SuperOpsValidationError("Days threshold must be >= 1")

        self.logger.debug(f"Getting contracts expiring within {days_threshold} days")

        # Calculate expiry date threshold
        from datetime import datetime, timedelta

        expiry_threshold = datetime.now() + timedelta(days=days_threshold)

        filters = {
            "status": ContractStatus.ACTIVE.value,
            "endDateBefore": expiry_threshold.isoformat(),
        }
        if client_id:
            filters["clientId"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="endDate",
            sort_order="asc",
        )

    async def get_renewal_pending_contracts(
        self,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get contracts with renewal pending status.

        Args:
            client_id: Optional client ID to filter by
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[Contract]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        self.logger.debug("Getting contracts with renewal pending")

        filters = {"status": ContractStatus.RENEWAL_PENDING.value}
        if client_id:
            filters["clientId"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="renewalDate",
            sort_order="asc",
        )

    async def get_contracts_by_type(
        self,
        contract_type: ContractType,
        client_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Get contracts by type.

        Args:
            contract_type: Contract type to filter by
            client_id: Optional client ID to filter by
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Dictionary containing 'items' (List[Contract]) and 'pagination' info

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not isinstance(contract_type, ContractType):
            raise SuperOpsValidationError("Contract type must be a ContractType enum")

        self.logger.debug(f"Getting contracts by type: {contract_type.value}")

        filters = {"contractType": contract_type.value}
        if client_id:
            filters["clientId"] = client_id

        return await self.list(
            page=page,
            page_size=page_size,
            filters=filters,
            sort_by="name",
            sort_order="asc",
        )

    async def activate_contract(self, contract_id: str) -> Contract:
        """Activate a contract.

        Args:
            contract_id: The contract ID

        Returns:
            Updated contract instance

        Raises:
            SuperOpsValidationError: If contract_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If contract doesn't exist
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Activating contract: {contract_id}")

        return await self.update(contract_id, {"status": ContractStatus.ACTIVE.value})

    async def suspend_contract(self, contract_id: str) -> Contract:
        """Suspend a contract.

        Args:
            contract_id: The contract ID

        Returns:
            Updated contract instance

        Raises:
            SuperOpsValidationError: If contract_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If contract doesn't exist
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Suspending contract: {contract_id}")

        return await self.update(contract_id, {"status": ContractStatus.SUSPENDED.value})

    async def cancel_contract(
        self, contract_id: str, cancellation_reason: Optional[str] = None
    ) -> Contract:
        """Cancel a contract.

        Args:
            contract_id: The contract ID
            cancellation_reason: Optional reason for cancellation

        Returns:
            Updated contract instance

        Raises:
            SuperOpsValidationError: If contract_id is invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If contract doesn't exist
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")

        self.logger.debug(f"Cancelling contract: {contract_id}")

        update_data = {"status": ContractStatus.CANCELLED.value}
        if cancellation_reason:
            update_data["cancellationReason"] = cancellation_reason

        return await self.update(contract_id, update_data)

    async def renew_contract(
        self,
        contract_id: str,
        new_end_date: datetime,
        new_contract_value: Optional[float] = None,
    ) -> Contract:
        """Renew a contract with new end date and optional new value.

        Args:
            contract_id: The contract ID
            new_end_date: New end date for the contract
            new_contract_value: Optional new contract value

        Returns:
            Updated contract instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If contract doesn't exist
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")
        if not isinstance(new_end_date, datetime):
            raise SuperOpsValidationError("New end date must be a datetime object")
        if new_end_date <= datetime.now():
            raise SuperOpsValidationError("New end date must be in the future")

        self.logger.debug(f"Renewing contract: {contract_id}")

        update_data = {
            "endDate": new_end_date.isoformat(),
            "status": ContractStatus.ACTIVE.value,
            "renewalDate": None,  # Clear renewal date
        }

        if new_contract_value is not None:
            if new_contract_value < 0:
                raise SuperOpsValidationError("Contract value must be >= 0")
            update_data["contractValue"] = new_contract_value

        return await self.update(contract_id, update_data)

    async def set_renewal_pending(self, contract_id: str, renewal_date: datetime) -> Contract:
        """Set contract status to renewal pending.

        Args:
            contract_id: The contract ID
            renewal_date: Date when renewal should be processed

        Returns:
            Updated contract instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
            SuperOpsResourceNotFoundError: If contract doesn't exist
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")
        if not isinstance(renewal_date, datetime):
            raise SuperOpsValidationError("Renewal date must be a datetime object")

        self.logger.debug(f"Setting contract renewal pending: {contract_id}")

        return await self.update(
            contract_id,
            {
                "status": ContractStatus.RENEWAL_PENDING.value,
                "renewalDate": renewal_date.isoformat(),
            },
        )

    async def add_sla(self, contract_id: str, sla_data: Dict[str, Any]) -> ContractSLA:
        """Add an SLA to a contract.

        Args:
            contract_id: The contract ID
            sla_data: SLA data

        Returns:
            Created SLA instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")
        if not sla_data:
            raise SuperOpsValidationError("SLA data cannot be empty")

        self.logger.debug(f"Adding SLA to contract: {contract_id}")

        # Validate SLA data
        validated_data = self._validate_sla_data(sla_data)
        validated_data["contractId"] = contract_id

        mutation = self._build_create_sla_mutation()
        variables = {"input": validated_data}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsValidationError("No data returned when creating SLA")

        sla_data = response["data"].get("createContractSLA")
        if not sla_data:
            raise SuperOpsValidationError("No SLA data in create response")

        return ContractSLA.from_dict(sla_data)

    async def add_rate(self, contract_id: str, rate_data: Dict[str, Any]) -> ContractRate:
        """Add a billing rate to a contract.

        Args:
            contract_id: The contract ID
            rate_data: Rate data

        Returns:
            Created rate instance

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If the API request fails
        """
        if not contract_id or not isinstance(contract_id, str):
            raise SuperOpsValidationError(f"Invalid contract ID: {contract_id}")
        if not rate_data:
            raise SuperOpsValidationError("Rate data cannot be empty")

        self.logger.debug(f"Adding rate to contract: {contract_id}")

        # Validate rate data
        validated_data = self._validate_rate_data(rate_data)
        validated_data["contractId"] = contract_id

        mutation = self._build_create_rate_mutation()
        variables = {"input": validated_data}

        response = await self.client.execute_mutation(mutation, variables)

        if not response.get("data"):
            raise SuperOpsValidationError("No data returned when creating rate")

        rate_data = response["data"].get("createContractRate")
        if not rate_data:
            raise SuperOpsValidationError("No rate data in create response")

        return ContractRate.from_dict(rate_data)

    async def bulk_update_status(
        self, contract_ids: List[str], status: ContractStatus
    ) -> List[Contract]:
        """Update status for multiple contracts.

        Args:
            contract_ids: List of contract IDs
            status: New status for all contracts

        Returns:
            List of updated contract instances

        Raises:
            SuperOpsValidationError: If parameters are invalid
            SuperOpsAPIError: If any API request fails
        """
        if not contract_ids:
            raise SuperOpsValidationError("Contract IDs list cannot be empty")
        if not isinstance(contract_ids, list):
            raise SuperOpsValidationError("Contract IDs must be a list")
        if not isinstance(status, ContractStatus):
            raise SuperOpsValidationError("Status must be a ContractStatus enum")

        self.logger.debug(
            f"Bulk updating status for {len(contract_ids)} contracts to {status.value}"
        )

        updated_contracts = []
        for contract_id in contract_ids:
            try:
                updated_contract = await self.update(contract_id, {"status": status.value})
                updated_contracts.append(updated_contract)
            except Exception as e:
                self.logger.error(f"Failed to update contract {contract_id}: {e}")
                # Continue with other contracts

        self.logger.info(
            f"Successfully updated {len(updated_contracts)} out of {len(contract_ids)} contracts"
        )
        return updated_contracts

    # Protected methods for GraphQL query building

    def _build_get_query(self, **kwargs) -> str:
        """Build GraphQL query for getting a single contract."""
        include_slas = kwargs.get("include_slas", False)
        include_rates = kwargs.get("include_rates", False)

        fields = [
            "id",
            "clientId",
            "name",
            "contractNumber",
            "contractType",
            "status",
            "startDate",
            "endDate",
            "renewalDate",
            "autoRenew",
            "billingCycle",
            "contractValue",
            "currency",
            "description",
            "termsAndConditions",
            "renewalTerms",
            "cancellationTerms",
            "signedByClient",
            "signedByProvider",
            "signedDate",
            "notificationDays",
            "tags",
            "customFields",
            "createdAt",
            "updatedAt",
        ]

        if include_slas:
            fields.append(
                """
                slas {
                    id
                    level
                    responseTimeMinutes
                    resolutionTimeHours
                    availabilityPercentage
                    description
                    penalties
                    createdAt
                    updatedAt
                }
            """
            )

        if include_rates:
            fields.append(
                """
                rates {
                    id
                    serviceType
                    rateType
                    rateAmount
                    currency
                    description
                    effectiveDate
                    endDate
                    createdAt
                    updatedAt
                }
            """
            )

        field_str = "\n        ".join(fields)

        return f"""
            query GetContract($id: ID!) {{
                contract(id: $id) {{
                    {field_str}
                }}
            }}
        """

    def _build_list_query(self, **kwargs) -> str:
        """Build GraphQL query for listing contracts."""
        return """
            query ListContracts(
                $page: Int!
                $pageSize: Int!
                $filters: ContractFilter
                $sortBy: String
                $sortOrder: SortOrder
            ) {
                contracts(
                    page: $page
                    pageSize: $pageSize
                    filters: $filters
                    sortBy: $sortBy
                    sortOrder: $sortOrder
                ) {
                    items {
                        id
                        clientId
                        name
                        contractNumber
                        contractType
                        status
                        startDate
                        endDate
                        renewalDate
                        autoRenew
                        billingCycle
                        contractValue
                        currency
                        description
                        tags
                        createdAt
                        updatedAt
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
        """

    def _build_create_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for creating a contract."""
        return """
            mutation CreateContract($input: CreateContractInput!) {
                createContract(input: $input) {
                    id
                    clientId
                    name
                    contractNumber
                    contractType
                    status
                    startDate
                    endDate
                    renewalDate
                    autoRenew
                    billingCycle
                    contractValue
                    currency
                    description
                    termsAndConditions
                    renewalTerms
                    cancellationTerms
                    signedByClient
                    signedByProvider
                    signedDate
                    notificationDays
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_update_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for updating a contract."""
        return """
            mutation UpdateContract($id: ID!, $input: UpdateContractInput!) {
                updateContract(id: $id, input: $input) {
                    id
                    clientId
                    name
                    contractNumber
                    contractType
                    status
                    startDate
                    endDate
                    renewalDate
                    autoRenew
                    billingCycle
                    contractValue
                    currency
                    description
                    termsAndConditions
                    renewalTerms
                    cancellationTerms
                    signedByClient
                    signedByProvider
                    signedDate
                    notificationDays
                    tags
                    customFields
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_delete_mutation(self, **kwargs) -> str:
        """Build GraphQL mutation for deleting a contract."""
        return """
            mutation DeleteContract($id: ID!) {
                deleteContract(id: $id) {
                    success
                    message
                }
            }
        """

    def _build_search_query(self, **kwargs) -> str:
        """Build GraphQL query for searching contracts."""
        return """
            query SearchContracts(
                $query: String!
                $page: Int!
                $pageSize: Int!
            ) {
                searchContracts(
                    query: $query
                    page: $page
                    pageSize: $pageSize
                ) {
                    items {
                        id
                        clientId
                        name
                        contractNumber
                        contractType
                        status
                        startDate
                        endDate
                        renewalDate
                        autoRenew
                        billingCycle
                        contractValue
                        currency
                        description
                        tags
                        createdAt
                        updatedAt
                    }
                    pagination {
                        page
                        pageSize
                        total
                        hasNextPage
                        hasPreviousPage
                    }
                }
            }
        """

    def _build_create_sla_mutation(self) -> str:
        """Build GraphQL mutation for creating a contract SLA."""
        return """
            mutation CreateContractSLA($input: CreateContractSLAInput!) {
                createContractSLA(input: $input) {
                    id
                    contractId
                    level
                    responseTimeMinutes
                    resolutionTimeHours
                    availabilityPercentage
                    description
                    penalties
                    createdAt
                    updatedAt
                }
            }
        """

    def _build_create_rate_mutation(self) -> str:
        """Build GraphQL mutation for creating a contract rate."""
        return """
            mutation CreateContractRate($input: CreateContractRateInput!) {
                createContractRate(input: $input) {
                    id
                    contractId
                    serviceType
                    rateType
                    rateAmount
                    currency
                    description
                    effectiveDate
                    endDate
                    createdAt
                    updatedAt
                }
            }
        """

    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for contract creation."""
        validated = data.copy()

        # Validate required fields
        self._validate_required_fields(validated)

        # Validate enum fields
        self._validate_enum_fields(validated)

        # Validate dates and numeric values
        self._validate_dates_and_values(validated)

        return validated

    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """Validate required fields for contract creation."""
        required_fields = ["clientId", "name", "contractType", "startDate"]
        error_messages = {
            "clientId": "Client ID is required",
            "name": "Contract name is required",
            "contractType": "Contract type is required",
            "startDate": "Start date is required",
        }

        for field in required_fields:
            if not data.get(field):
                raise SuperOpsValidationError(error_messages[field])

    def _validate_enum_fields(self, data: Dict[str, Any]) -> None:
        """Validate enum fields for contract creation."""
        enum_validations = [
            ("contractType", ContractType, "Invalid contract type"),
            ("status", ContractStatus, "Invalid contract status"),
            ("billingCycle", BillingCycle, "Invalid billing cycle"),
        ]

        for field_name, enum_class, error_msg in enum_validations:
            value = data.get(field_name)
            if value and value not in [e.value for e in enum_class]:
                raise SuperOpsValidationError(f"{error_msg}: {value}")

    def _validate_dates_and_values(self, data: Dict[str, Any]) -> None:
        """Validate dates and numeric values for contract creation."""
        # Validate contract value
        contract_value = data.get("contractValue")
        if contract_value is not None and contract_value < 0:
            raise SuperOpsValidationError("Contract value must be >= 0")

        # Validate date relationship
        start_date = data.get("startDate")
        end_date = data.get("endDate")
        if start_date and end_date:
            start_dt = self._parse_date_string(start_date)
            end_dt = self._parse_date_string(end_date)
            if end_dt <= start_dt:
                raise SuperOpsValidationError("End date must be after start date")

    def _parse_date_string(self, date_value):
        """Parse date string to datetime object."""
        if isinstance(date_value, str):
            return datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return date_value

    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for contract updates."""
        validated = data.copy()

        # Validate contract type if provided
        contract_type = validated.get("contractType")
        if contract_type and contract_type not in [t.value for t in ContractType]:
            raise SuperOpsValidationError(f"Invalid contract type: {contract_type}")

        # Validate status if provided
        status = validated.get("status")
        if status and status not in [s.value for s in ContractStatus]:
            raise SuperOpsValidationError(f"Invalid contract status: {status}")

        # Validate billing cycle if provided
        billing_cycle = validated.get("billingCycle")
        if billing_cycle and billing_cycle not in [c.value for c in BillingCycle]:
            raise SuperOpsValidationError(f"Invalid billing cycle: {billing_cycle}")

        # Validate contract value if provided
        contract_value = validated.get("contractValue")
        if contract_value is not None and contract_value < 0:
            raise SuperOpsValidationError("Contract value must be >= 0")

        return validated

    def _validate_sla_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SLA data."""
        validated = data.copy()

        # Required fields
        if not validated.get("level"):
            raise SuperOpsValidationError("SLA level is required")

        # Validate SLA level
        level = validated.get("level")
        if level and level not in [sla_level.value for sla_level in SLALevel]:
            raise SuperOpsValidationError(f"Invalid SLA level: {level}")

        # Validate time values
        response_time = validated.get("responseTimeMinutes")
        if response_time is not None and response_time < 0:
            raise SuperOpsValidationError("Response time must be >= 0")

        resolution_time = validated.get("resolutionTimeHours")
        if resolution_time is not None and resolution_time < 0:
            raise SuperOpsValidationError("Resolution time must be >= 0")

        availability = validated.get("availabilityPercentage")
        if availability is not None and (availability < 0 or availability > 100):
            raise SuperOpsValidationError("Availability percentage must be between 0 and 100")

        return validated

    def _validate_rate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rate data."""
        validated = data.copy()

        # Required fields
        if not validated.get("serviceType"):
            raise SuperOpsValidationError("Service type is required")
        if not validated.get("rateType"):
            raise SuperOpsValidationError("Rate type is required")
        if validated.get("rateAmount") is None:
            raise SuperOpsValidationError("Rate amount is required")

        # Validate rate amount
        rate_amount = validated.get("rateAmount")
        if rate_amount < 0:
            raise SuperOpsValidationError("Rate amount must be >= 0")

        return validated
