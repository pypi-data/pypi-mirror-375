# py-superops Test Suite

This directory contains comprehensive tests for the py-superops client library.

## Test Structure

### Core Tests
- **`test_foundation.py`** - Tests for core components (Config, Auth, Client, Exceptions)
- **`test_graphql.py`** - Tests for GraphQL utilities (Types, Builders, Queries, Fragments)
- **`test_managers.py`** - Tests for resource managers and CRUD operations

### Advanced Tests
- **`test_integration.py`** - End-to-end integration tests and workflows
- **`test_edge_cases.py`** - Edge cases, error scenarios, and robustness testing

### Test Configuration
- **`conftest.py`** - Shared test fixtures, mock factories, and test utilities

## Test Coverage

###  Working Tests (83 passing)

#### Foundation Tests (27 tests)
- Configuration creation and validation
- Authentication handler functionality
- SuperOps client initialization
- Exception handling
- Convenience functions
- Package integrity checks

#### GraphQL Tests (37 tests)
- Type validation and serialization
- Fragment string generation and dependency resolution
- Query and mutation builders
- Common query patterns
- Integration workflows

#### Manager Tests (19 tests)
- Base ResourceManager CRUD operations
- Data validation and error handling
- Mock verification and response processing
- Pagination and filtering

### =§ Tests Needing Fixes

#### Integration Tests (16 failed, 1 passed)
- **Issue**: Mock setup for async HTTP operations needs improvement
- **Status**: Test framework is working but needs better async mocking
- **Next Steps**: Fix mock configuration for httpx AsyncClient

#### Edge Case Tests
- **Status**: Most tests working, minor fixes needed for config validation

## Running Tests

### Quick Test Run
```bash
# Run core working tests
pytest tests/test_foundation.py tests/test_graphql.py tests/test_managers.py::TestResourceManager -v

# Run specific test categories
pytest tests/test_foundation.py -v
pytest tests/test_graphql.py -v
```

### Full Test Suite
```bash
# Run all tests (some integration tests will fail)
pytest tests/ -v

# Run with coverage
pytest tests/test_foundation.py tests/test_graphql.py --cov=src/py_superops
```

### Test Categories

#### Unit Tests
-  Configuration validation
-  Authentication handling  
-  GraphQL query building
-  Data type validation
-  Manager CRUD operations

#### Integration Tests
- =§ End-to-end workflows (needs mock fixes)
- =§ Cross-manager operations (needs mock fixes)
-  Error handling integration

#### Edge Case Tests  
-  Configuration edge cases
- =§ Network error simulation (needs mock fixes)
-  Data validation edge cases

## Test Fixtures

The `conftest.py` file provides comprehensive test fixtures:

### Configuration Fixtures
- `test_config` - Standard test configuration
- `eu_config` - EU datacenter configuration
- `auth_handler` - Authentication handler instance

### Mock Fixtures
- `mock_http_client` - AsyncMock for httpx client
- `mock_httpx_response` - Factory for mock HTTP responses
- `mock_success_response` - Standard success response
- `mock_error_response` - Standard error response

### Data Fixtures
- `sample_client_data` - Test client data
- `sample_ticket_data` - Test ticket data  
- `sample_asset_data` - Test asset data
- And more for contacts, sites, knowledge base

### Utility Fixtures
- `performance_timer` - Performance measurement
- `assert_valid_graphql_query` - GraphQL validation
- `network_error`, `timeout_error` - Error simulation

## Test Quality Features

### Comprehensive Assertions
- Validates return values and types
- Checks GraphQL query structure
- Verifies mock call arguments
- Tests error message content

### Performance Testing
- Concurrent operation testing
- Large dataset handling
- Response time measurement

### Error Scenario Testing
- Network failures
- Authentication errors  
- Rate limiting
- Validation errors
- Resource not found

### Edge Case Coverage
- Unicode handling
- Extreme configuration values
- Malformed responses
- Memory management

## Development Guidelines

### Adding New Tests
1. Use appropriate test file (`test_foundation.py`, `test_graphql.py`, etc.)
2. Leverage existing fixtures from `conftest.py`
3. Follow naming conventions: `test_<component>_<scenario>`
4. Include both positive and negative test cases
5. Add docstrings explaining test purpose

### Mock Usage
- Use `AsyncMock` for async operations
- Verify mock calls with `assert_called_with()`
- Reset mocks between tests using fixtures
- Create realistic mock data

### Test Organization
- Group related tests in classes
- Use descriptive test and class names
- Add module-level docstrings
- Separate unit, integration, and edge case tests

## Known Issues

### Integration Test Mocking
The integration tests currently fail because the async mock setup needs improvement. The core issue is properly mocking `httpx.AsyncClient` operations.

### Potential Fixes
1. Better async context manager mocking
2. Improved response object simulation
3. More realistic async operation flows

Despite these integration test issues, the core functionality is well-tested with 83 passing tests covering all major components.
