SuperOps Client API
===================

The :class:`~py_superops.client.SuperOpsClient` is the main entry point for interacting with the SuperOps GraphQL API. It provides low-level GraphQL operations and high-level manager interfaces.

Overview
--------

The SuperOpsClient provides:

- **GraphQL Operations**: Direct query and mutation execution
- **Manager Access**: High-level interfaces for all SuperOps resources
- **Connection Management**: Automatic connection pooling and cleanup
- **Error Handling**: Comprehensive exception handling
- **Rate Limiting**: Built-in rate limiting and retry logic
- **Caching**: Optional response caching for improved performance

Basic Usage
-----------

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def main():
       config = SuperOpsConfig.from_env()

       # Method 1: Using async context manager (recommended)
       async with SuperOpsClient(config) as client:
           connection_info = await client.test_connection()
           print(f"Connected: {connection_info['connected']}")

       # Method 2: Manual lifecycle management
       client = SuperOpsClient(config)
       try:
           connection_info = await client.test_connection()
           print(f"Connected: {connection_info['connected']}")
       finally:
           await client.close()

   asyncio.run(main())

Class Reference
---------------

.. autoclass:: py_superops.client.SuperOpsClient
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __init__, __aenter__, __aexit__

Advanced Usage
--------------

Batch Operations
^^^^^^^^^^^^^^^^

Execute multiple operations efficiently:

.. code-block:: python

   async def batch_operations():
       async with SuperOpsClient(config) as client:
           # Prepare multiple operations
           operations = []

           # Add query operations
           operations.append({
               'query': 'query { clients(limit: 10) { id name } }',
               'variables': {}
           })

           operations.append({
               'query': 'query { tickets(limit: 5) { id title } }',
               'variables': {}
           })

           # Execute batch (if supported by API)
           # Note: This is a conceptual example
           results = await client.execute_batch(operations)

           clients = results[0]['data']['clients']
           tickets = results[1]['data']['tickets']

Custom Headers and Request Modification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from py_superops import SuperOpsClient, SuperOpsConfig

   async def custom_request_example():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Access the underlying HTTP client if needed
           custom_headers = {
               'X-Custom-Header': 'custom-value',
               'X-Request-ID': 'req-123'
           }

           # For advanced users: modify request headers
           original_headers = client._http_client.headers
           client._http_client.headers.update(custom_headers)

           try:
               response = await client.execute_query('query { me { name } }')
               print(f"User: {response['data']['me']['name']}")
           finally:
               # Restore original headers
               client._http_client.headers = original_headers

Caching and Performance
^^^^^^^^^^^^^^^^^^^^^^^

Enable response caching for better performance:

.. code-block:: python

   from py_superops import SuperOpsConfig

   config = SuperOpsConfig(
       api_key="your-api-key"  # pragma: allowlist secret,
       enable_caching=True,
       cache_ttl=300,  # Cache for 5 minutes
       cache_max_size=1000  # Max 1000 cached responses
   )

   async with SuperOpsClient(config) as client:
       # First call hits the API
       clients1 = await client.execute_query('query { clients(limit: 10) { id name } }')

       # Second call returns cached result (if within TTL)
       clients2 = await client.execute_query('query { clients(limit: 10) { id name } }')

       # Cache is automatically managed

Error Handling Patterns
-----------------------

Comprehensive error handling:

.. code-block:: python

   from py_superops import (
       SuperOpsClient,
       SuperOpsConfig,
       SuperOpsAPIError,
       SuperOpsAuthenticationError,
       SuperOpsNetworkError,
       SuperOpsRateLimitError,
       SuperOpsValidationError,
       SuperOpsTimeoutError
   )

   async def robust_client_usage():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           try:
               # Test connection first
               await client.test_connection()

               # Execute operations
               query = 'query { clients { id name } }'
               response = await client.execute_query(query)

           except SuperOpsAuthenticationError:
               print("❌ Invalid API credentials")
               # Handle authentication failure

           except SuperOpsRateLimitError as e:
               print(f"⏳ Rate limited. Retry after {e.retry_after}s")
               # Implement backoff strategy

           except SuperOpsValidationError as e:
               print(f"📝 Invalid query: {e.message}")
               # Fix query syntax

           except SuperOpsTimeoutError:
               print("⏱️ Request timed out")
               # Retry with longer timeout

           except SuperOpsNetworkError as e:
               print(f"🌐 Network error: {e.message}")
               # Check network connectivity

           except SuperOpsAPIError as e:
               print(f"🚫 API error: {e.message} (status: {e.status_code})")
               # Handle specific API errors

           except Exception as e:
               print(f"💥 Unexpected error: {e}")
               # Handle unexpected errors

Rate Limiting and Retries
-------------------------

The client includes built-in rate limiting and retry logic:

.. code-block:: python

   from py_superops import SuperOpsConfig

   config = SuperOpsConfig(
       api_key="your-api-key"  # pragma: allowlist secret,
       rate_limit_per_minute=60,    # Max 60 requests per minute
       max_retries=3,               # Retry failed requests up to 3 times
       retry_delay=1.0,             # Initial retry delay
       retry_exponential_base=2.0,  # Exponential backoff multiplier
   )

   async with SuperOpsClient(config) as client:
       # Client automatically handles rate limiting and retries
       for i in range(100):  # Many requests
           try:
               response = await client.execute_query('query { me { name } }')
               print(f"Request {i+1}: {response['data']['me']['name']}")
           except SuperOpsRateLimitError:
               print(f"Rate limited on request {i+1}")
               break

Connection Pooling
------------------

The client uses connection pooling for optimal performance:

.. code-block:: python

   from py_superops import SuperOpsConfig

   config = SuperOpsConfig(
       api_key="your-api-key"  # pragma: allowlist secret,
       max_connections=20,      # Max concurrent connections
       max_keepalive=10,        # Max keep-alive connections
       keepalive_timeout=30.0,  # Keep-alive timeout
   )

   async with SuperOpsClient(config) as client:
       # Concurrent requests share connection pool
       import asyncio

       async def make_request(i):
           query = f'query {{ clients(limit: 1, offset: {i}) {{ id name }} }}'
           return await client.execute_query(query)

       # Execute multiple requests concurrently
       tasks = [make_request(i) for i in range(10)]
       results = await asyncio.gather(*tasks)

       print(f"Completed {len(results)} concurrent requests")

Debugging and Logging
---------------------

Enable debug mode for detailed logging:

.. code-block:: python

   from py_superops import SuperOpsConfig
   import logging

   # Configure logging
   logging.basicConfig(level=logging.DEBUG)

   config = SuperOpsConfig(
       api_key="your-api-key"  # pragma: allowlist secret,
       debug=True  # Enable debug logging
   )

   async with SuperOpsClient(config) as client:
       # Debug logs will show:
       # - HTTP requests and responses
       # - GraphQL queries and variables
       # - Rate limiting information
       # - Cache hits/misses

       response = await client.execute_query('query { me { name } }')

Best Practices
--------------

1. **Use Context Manager**: Always use ``async with`` for proper resource cleanup
2. **Test Connection**: Call ``test_connection()`` before performing operations
3. **Handle Errors**: Implement comprehensive error handling
4. **Use Managers**: Prefer high-level managers over raw GraphQL for common operations
5. **Enable Caching**: Use caching for frequently accessed, stable data
6. **Monitor Rate Limits**: Respect rate limits to avoid service disruption
7. **Pool Connections**: Use connection pooling for concurrent requests

Performance Considerations
--------------------------

- **Batch Operations**: Group related operations when possible
- **Field Selection**: Only request needed fields in GraphQL queries
- **Pagination**: Use appropriate page sizes for large datasets
- **Caching**: Cache stable data to reduce API calls
- **Connection Reuse**: Keep client instances alive for multiple operations

.. code-block:: python

   # Good: Efficient field selection
   query = '''
   query GetClients {
       clients(limit: 100) {
           id
           name
           # Only select fields you need
       }
   }
   '''

   # Good: Reuse client for multiple operations
   async with SuperOpsClient(config) as client:
       # Multiple operations with same client
       clients = await client.clients.get_active_clients()
       tickets = await client.tickets.get_open_tickets()
       assets = await client.assets.get_warranty_expiring_soon()

Related Documentation
---------------------

- :doc:`config` - Configuration options
- :doc:`managers` - High-level manager interfaces
- :doc:`exceptions` - Error handling and exceptions
- :doc:`../guide/async-patterns` - Async programming patterns
- :doc:`../guide/best-practices` - Best practices guide
