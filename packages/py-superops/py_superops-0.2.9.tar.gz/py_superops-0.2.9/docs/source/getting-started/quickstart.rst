Quickstart Guide
================

This guide will get you up and running with py-superops in just a few minutes. We'll cover basic setup, authentication, and your first API calls.

Prerequisites
-------------

Before starting, make sure you have:

- Python 3.8+ installed
- py-superops installed (see :doc:`installation`)
- A SuperOps account and API key

.. tip::
   If you don't have a SuperOps API key yet, log into your SuperOps account and navigate to
   Settings → API Keys to generate one.

Your First py-superops Script
-----------------------------

Let's create a simple script to test the connection and fetch some data:

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def main():
       # Create configuration (replace with your API key)
       config = SuperOpsConfig(
           api_key="your-api-key-here",  # pragma: allowlist secret
           base_url="https://api.superops.com/v1"
       )

       # Create client and test connection
       async with SuperOpsClient(config) as client:
           try:
               # Test the connection
               connection_info = await client.test_connection()
               print(f"✅ Connected to SuperOps API!")
               print(f"   Status: {connection_info['connected']}")
               print(f"   User: {connection_info.get('user', {}).get('name', 'Unknown')}")

           except Exception as e:
               print(f"❌ Connection failed: {e}")
               return

   if __name__ == "__main__":
       asyncio.run(main())

Save this as ``test_connection.py`` and run it:

.. code-block:: bash

   python test_connection.py

If successful, you should see output like:

.. code-block:: text

   ✅ Connected to SuperOps API!
      Status: True
      User: Your Name

Environment Variables Setup
---------------------------

For security, it's better to use environment variables for sensitive data:

1. Create a ``.env`` file in your project directory:

.. code-block:: bash

   # .env file
   SUPEROPS_API_KEY=your-api-key-here
   SUPEROPS_BASE_URL=https://api.superops.com/v1

2. Update your script to use environment configuration:

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def main():
       # Load configuration from environment variables
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           connection_info = await client.test_connection()
           print(f"Connected: {connection_info['connected']}")

   if __name__ == "__main__":
       asyncio.run(main())

3. Run with environment variables loaded:

.. code-block:: bash

   # Load .env file and run (if using python-dotenv)
   python -c "from dotenv import load_dotenv; load_dotenv()" && python your_script.py

   # Or export variables manually
   export SUPEROPS_API_KEY="your-api-key-here"
   export SUPEROPS_BASE_URL="https://api.superops.com/v1"
   python your_script.py

Basic Data Retrieval
---------------------

Now let's fetch some actual data using the high-level managers:

Client Management
^^^^^^^^^^^^^^^^^

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def get_clients_example():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Get active clients
           clients_response = await client.clients.get_active_clients(page_size=10)

           print(f"Found {len(clients_response['items'])} active clients:")

           for client_data in clients_response['items']:
               print(f"  • {client_data.name} ({client_data.email})")

           # Get a specific client by ID
           if clients_response['items']:
               first_client = clients_response['items'][0]
               client_details = await client.clients.get_by_id(first_client.id)
               print(f"\nClient details: {client_details.name}")
               print(f"  Status: {client_details.status}")
               print(f"  Created: {client_details.created_at}")

   asyncio.run(get_clients_example())

Ticket Management
^^^^^^^^^^^^^^^^^

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def get_tickets_example():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Get open tickets
           tickets_response = await client.tickets.get_open_tickets(page_size=5)

           print(f"Found {len(tickets_response['items'])} open tickets:")

           for ticket in tickets_response['items']:
               print(f"  • #{ticket.number}: {ticket.title}")
               print(f"    Priority: {ticket.priority}, Status: {ticket.status}")
               print(f"    Client: {ticket.client.name if ticket.client else 'N/A'}")
               print()

   asyncio.run(get_tickets_example())

Asset Tracking
^^^^^^^^^^^^^^

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def get_assets_example():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Get assets with expiring warranties
           expiring_assets = await client.assets.get_warranty_expiring_soon(
               days_threshold=30  # Assets expiring within 30 days
           )

           print(f"Found {len(expiring_assets['items'])} assets with expiring warranties:")

           for asset in expiring_assets['items']:
               print(f"  • {asset.name} ({asset.asset_type})")
               print(f"    Client: {asset.client.name if asset.client else 'N/A'}")
               print(f"    Warranty expires: {asset.warranty_expiry_date}")
               print()

   asyncio.run(get_assets_example())

Error Handling
--------------

Always include proper error handling in production code:

.. code-block:: python

   import asyncio
   from py_superops import (
       SuperOpsClient,
       SuperOpsConfig,
       SuperOpsAPIError,
       SuperOpsAuthenticationError,
       SuperOpsNetworkError,
       SuperOpsRateLimitError
   )

   async def robust_example():
       config = SuperOpsConfig.from_env()

       try:
           async with SuperOpsClient(config) as client:
               # Test connection first
               await client.test_connection()
               print("✅ Connection successful")

               # Perform operations
               clients = await client.clients.get_active_clients()
               print(f"Retrieved {len(clients['items'])} clients")

       except SuperOpsAuthenticationError:
           print("❌ Authentication failed - check your API key")
       except SuperOpsRateLimitError as e:
           print(f"❌ Rate limit exceeded - retry after {e.retry_after} seconds")
       except SuperOpsNetworkError:
           print("❌ Network error - check your connection")
       except SuperOpsAPIError as e:
           print(f"❌ API error: {e.message} (status: {e.status_code})")
       except Exception as e:
           print(f"❌ Unexpected error: {e}")

   asyncio.run(robust_example())

Using Raw GraphQL Queries
--------------------------

While managers provide convenient high-level interfaces, you can also use raw GraphQL queries:

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def raw_graphql_example():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Custom GraphQL query
           query = '''
           query GetClientsWithSites($limit: Int) {
               clients(limit: $limit) {
                   id
                   name
                   email
                   status
                   sites {
                       id
                       name
                       address
                   }
               }
           }
           '''

           variables = {"limit": 5}

           response = await client.execute_query(query, variables=variables)
           clients = response['data']['clients']

           for client_data in clients:
               print(f"Client: {client_data['name']}")
               print(f"  Email: {client_data['email']}")
               print(f"  Sites: {len(client_data['sites'])}")
               for site in client_data['sites']:
                   print(f"    - {site['name']} ({site['address']})")
               print()

   asyncio.run(raw_graphql_example())

Configuration Options
---------------------

SuperOps client supports various configuration options:

.. code-block:: python

   from py_superops import SuperOpsConfig

   # Detailed configuration
   config = SuperOpsConfig(
       api_key="your-api-key",  # pragma: allowlist secret
       base_url="https://api.superops.com/v1",
       timeout=30.0,          # Request timeout in seconds
       max_retries=3,         # Maximum retry attempts
       rate_limit_per_minute=60,  # Rate limiting
       enable_caching=True,   # Response caching
       cache_ttl=300,         # Cache time-to-live in seconds
       debug=False           # Debug logging
   )

You can also load configuration from a YAML file:

.. code-block:: yaml

   # superops.yaml
   api_key: "your-api-key"
   base_url: "https://api.superops.com/v1"
   timeout: 30.0
   max_retries: 3
   enable_caching: true
   cache_ttl: 300

.. code-block:: python

   config = SuperOpsConfig.from_file("superops.yaml")

Next Steps
----------

Now that you have py-superops working, explore these areas:

1. **:doc:`configuration`** - Learn about all configuration options
2. **:doc:`authentication`** - Understand authentication and security
3. **:doc:`../guide/managers-overview`** - Explore all available managers
4. **:doc:`../examples/basic-usage`** - See more detailed examples
5. **:doc:`../guide/best-practices`** - Learn recommended practices

Common Use Cases
----------------

Here are some common patterns you might find useful:

**Daily Ticket Summary:**

.. code-block:: python

   async def daily_ticket_summary():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Get today's tickets
           open_tickets = await client.tickets.get_open_tickets()
           overdue_tickets = await client.tickets.get_overdue_tickets()

           print(f"📊 Daily Ticket Summary")
           print(f"  Open tickets: {len(open_tickets['items'])}")
           print(f"  Overdue tickets: {len(overdue_tickets['items'])}")

           if overdue_tickets['items']:
               print(f"\n⚠️  Overdue tickets need attention:")
               for ticket in overdue_tickets['items']:
                   print(f"    #{ticket.number}: {ticket.title}")

**Asset Warranty Monitoring:**

.. code-block:: python

   async def warranty_monitoring():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Check warranties expiring in next 90 days
           for days in [30, 60, 90]:
               assets = await client.assets.get_warranty_expiring_soon(
                   days_threshold=days
               )
               print(f"📋 Assets expiring within {days} days: {len(assets['items'])}")

**Client Health Check:**

.. code-block:: python

   async def client_health_check():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           clients = await client.clients.get_active_clients()

           for client_data in clients['items']:
               # Get client's open tickets
               client_tickets = await client.tickets.get_by_client_id(
                   client_data.id,
                   status="OPEN"
               )

               # Get client's assets
               client_assets = await client.assets.get_by_client_id(client_data.id)

               print(f"🏢 {client_data.name}")
               print(f"   Open tickets: {len(client_tickets['items'])}")
               print(f"   Assets: {len(client_assets['items'])}")

Troubleshooting
---------------

**Common Issues:**

1. **"Authentication failed"** - Check your API key and permissions
2. **"Network timeout"** - Increase timeout in configuration or check connectivity
3. **"Rate limit exceeded"** - Implement exponential backoff or reduce request frequency
4. **"Invalid GraphQL query"** - Use the schema introspection or check query syntax

**Getting Help:**

- Check the :doc:`../troubleshooting` guide
- Review the :doc:`../api/exceptions` documentation
- Search existing GitHub issues
- Create a new issue with detailed error information

You're now ready to start building with py-superops! 🎉
