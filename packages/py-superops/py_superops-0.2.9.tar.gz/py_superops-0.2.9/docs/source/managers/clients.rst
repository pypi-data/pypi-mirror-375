Client Manager
==============

The :class:`~py_superops.managers.ClientManager` provides comprehensive functionality for managing SuperOps clients (customers). This includes client lifecycle management, status updates, contact relationships, and bulk operations.

Overview
--------

The ClientManager handles all aspects of client management in SuperOps:

- **Client Discovery**: Find clients by various criteria
- **Status Management**: Activate, deactivate, and update client status
- **Relationship Management**: Handle contacts, sites, and projects
- **Bulk Operations**: Efficiently update multiple clients
- **Tag Management**: Organize clients with tags

Quick Start
-----------

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def client_examples():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Get all active clients
           active_clients = await client.clients.get_active_clients(page_size=50)
           print(f"Found {len(active_clients['items'])} active clients")

           # Find a specific client
           customer = await client.clients.get_by_email("admin@example.com")
           if customer:
               print(f"Found client: {customer.name}")

           # Update client status
           await client.clients.activate_client(customer.id)

   asyncio.run(client_examples())

Core Methods
------------

Client Retrieval
^^^^^^^^^^^^^^^^^

.. py:method:: get_active_clients(page_size: int = 50, page: int = 1) -> Dict[str, Any]

   Retrieve all active clients with pagination support.

   :param page_size: Number of clients per page (max 100)
   :param page: Page number to retrieve
   :returns: Dictionary with 'items' list and pagination info

   .. code-block:: python

      active_clients = await client.clients.get_active_clients(page_size=20)
      for client_data in active_clients['items']:
          print(f"Client: {client_data.name} ({client_data.email})")
          print(f"  Status: {client_data.status}")
          print(f"  Sites: {len(client_data.sites)} sites")

.. py:method:: get_by_id(client_id: str) -> Optional[Client]

   Get a client by their unique ID.

   :param client_id: The client's unique identifier
   :returns: Client object or None if not found

   .. code-block:: python

      client_data = await client.clients.get_by_id("client_123")
      if client_data:
          print(f"Client: {client_data.name}")
          print(f"Created: {client_data.created_at}")
          print(f"Last updated: {client_data.updated_at}")

.. py:method:: get_by_email(email: str) -> Optional[Client]

   Find a client by their primary email address.

   :param email: The client's email address
   :returns: Client object or None if not found

   .. code-block:: python

      client_data = await client.clients.get_by_email("admin@acme.com")
      if client_data:
          print(f"Found: {client_data.name}")
      else:
          print("Client not found")

.. py:method:: search_clients(query: str, limit: int = 20) -> Dict[str, Any]

   Search clients by name, email, or other text fields.

   :param query: Search terms
   :param limit: Maximum number of results
   :returns: Search results with matching clients

   .. code-block:: python

      results = await client.clients.search_clients("technology", limit=10)
      for client_data in results['items']:
          print(f"Match: {client_data.name} - {client_data.email}")

Status Management
^^^^^^^^^^^^^^^^^

.. py:method:: activate_client(client_id: str) -> bool

   Activate a client account.

   :param client_id: The client's unique identifier
   :returns: True if successful
   :raises SuperOpsAPIError: If activation fails

   .. code-block:: python

      success = await client.clients.activate_client("client_123")
      if success:
          print("Client activated successfully")

.. py:method:: deactivate_client(client_id: str) -> bool

   Deactivate a client account.

   :param client_id: The client's unique identifier
   :returns: True if successful
   :raises SuperOpsAPIError: If deactivation fails

   .. code-block:: python

      success = await client.clients.deactivate_client("client_123")
      if success:
          print("Client deactivated successfully")

.. py:method:: update_status(client_id: str, status: ClientStatus) -> bool

   Update a client's status.

   :param client_id: The client's unique identifier
   :param status: New status (ACTIVE, INACTIVE, SUSPENDED)
   :returns: True if successful

   .. code-block:: python

      from py_superops.graphql import ClientStatus

      success = await client.clients.update_status("client_123", ClientStatus.ACTIVE)
      if success:
          print("Status updated successfully")

Bulk Operations
^^^^^^^^^^^^^^^

.. py:method:: bulk_update_status(client_ids: List[str], status: ClientStatus) -> Dict[str, Any]

   Update status for multiple clients efficiently.

   :param client_ids: List of client IDs to update
   :param status: New status to apply
   :returns: Results with success/failure counts

   .. code-block:: python

      from py_superops.graphql import ClientStatus

      client_ids = ["client_1", "client_2", "client_3"]
      results = await client.clients.bulk_update_status(client_ids, ClientStatus.ACTIVE)

      print(f"Successfully updated: {results['successful']}")
      print(f"Failed updates: {results['failed']}")

.. py:method:: bulk_add_tags(client_ids: List[str], tags: List[str]) -> Dict[str, Any]

   Add tags to multiple clients.

   :param client_ids: List of client IDs
   :param tags: List of tags to add
   :returns: Results with success/failure counts

   .. code-block:: python

      client_ids = ["client_1", "client_2"]
      tags = ["premium", "priority-support"]

      results = await client.clients.bulk_add_tags(client_ids, tags)
      print(f"Tags added to {results['successful']} clients")

Tag Management
^^^^^^^^^^^^^^

.. py:method:: add_tag(client_id: str, tag: str) -> bool

   Add a tag to a client.

   :param client_id: The client's unique identifier
   :param tag: Tag to add
   :returns: True if successful

.. py:method:: remove_tag(client_id: str, tag: str) -> bool

   Remove a tag from a client.

   :param client_id: The client's unique identifier
   :param tag: Tag to remove
   :returns: True if successful

.. py:method:: get_tags(client_id: str) -> List[str]

   Get all tags for a client.

   :param client_id: The client's unique identifier
   :returns: List of tag names

   .. code-block:: python

      # Tag management example
      client_id = "client_123"

      # Add tags
      await client.clients.add_tag(client_id, "premium")
      await client.clients.add_tag(client_id, "priority-support")

      # Get all tags
      tags = await client.clients.get_tags(client_id)
      print(f"Client tags: {', '.join(tags)}")

      # Remove tag
      await client.clients.remove_tag(client_id, "premium")

Advanced Operations
-------------------

Client Analytics
^^^^^^^^^^^^^^^^

.. py:method:: get_client_metrics(client_id: str, days: int = 30) -> Dict[str, Any]

   Get performance metrics for a client.

   :param client_id: The client's unique identifier
   :param days: Number of days to analyze
   :returns: Metrics including tickets, assets, projects

   .. code-block:: python

      metrics = await client.clients.get_client_metrics("client_123", days=30)

      print(f"Last 30 days metrics:")
      print(f"  Tickets created: {metrics['tickets_created']}")
      print(f"  Tickets resolved: {metrics['tickets_resolved']}")
      print(f"  Average resolution time: {metrics['avg_resolution_hours']}h")
      print(f"  Assets monitored: {metrics['active_assets']}")

.. py:method:: get_client_health_score(client_id: str) -> Dict[str, Any]

   Calculate a health score for a client based on various factors.

   :param client_id: The client's unique identifier
   :returns: Health score and contributing factors

   .. code-block:: python

      health = await client.clients.get_client_health_score("client_123")

      print(f"Client health score: {health['score']}/100")
      print(f"Factors:")
      for factor, value in health['factors'].items():
          print(f"  {factor}: {value}")

Relationship Management
^^^^^^^^^^^^^^^^^^^^^^^

.. py:method:: get_client_contacts(client_id: str) -> List[Contact]

   Get all contacts associated with a client.

   :param client_id: The client's unique identifier
   :returns: List of contact objects

.. py:method:: get_client_sites(client_id: str) -> List[Site]

   Get all sites associated with a client.

   :param client_id: The client's unique identifier
   :returns: List of site objects

.. py:method:: get_client_projects(client_id: str, active_only: bool = True) -> List[Project]

   Get projects associated with a client.

   :param client_id: The client's unique identifier
   :param active_only: Whether to return only active projects
   :returns: List of project objects

   .. code-block:: python

      # Get client relationships
      client_id = "client_123"

      contacts = await client.clients.get_client_contacts(client_id)
      sites = await client.clients.get_client_sites(client_id)
      projects = await client.clients.get_client_projects(client_id)

      print(f"Client has {len(contacts)} contacts")
      print(f"Client has {len(sites)} sites")
      print(f"Client has {len(projects)} active projects")

Data Export
^^^^^^^^^^^

.. py:method:: export_client_data(client_id: str, format: str = "json") -> Dict[str, Any]

   Export comprehensive client data for backup or migration.

   :param client_id: The client's unique identifier
   :param format: Export format ("json", "csv")
   :returns: Exported data in requested format

   .. code-block:: python

      # Export client data
      client_data = await client.clients.export_client_data("client_123")

      print(f"Exported data includes:")
      for section, items in client_data.items():
          if isinstance(items, list):
              print(f"  {section}: {len(items)} items")

Common Use Cases
----------------

Client Onboarding Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   async def onboard_new_client(client_email: str):
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Check if client already exists
           existing_client = await client.clients.get_by_email(client_email)
           if existing_client:
               print(f"Client already exists: {existing_client.name}")
               return existing_client.id

           # Create new client (using raw GraphQL)
           mutation = '''
           mutation CreateClient($input: ClientInput!) {
               createClient(input: $input) {
                   id
                   name
                   email
                   status
               }
           }
           '''

           variables = {
               "input": {
                   "name": "New Client Corp",
                   "email": client_email,
                   "status": "ACTIVE"
               }
           }

           response = await client.execute_mutation(mutation, variables=variables)
           new_client = response['data']['createClient']

           # Add onboarding tags
           await client.clients.add_tag(new_client['id'], "new-client")
           await client.clients.add_tag(new_client['id'], "onboarding")

           print(f"Created new client: {new_client['name']}")
           return new_client['id']

Monthly Client Review
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   async def monthly_client_review():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           active_clients = await client.clients.get_active_clients(page_size=100)

           print("🏢 Monthly Client Review")
           print("=" * 50)

           for client_data in active_clients['items']:
               # Get client metrics
               metrics = await client.clients.get_client_metrics(client_data.id, days=30)
               health = await client.clients.get_client_health_score(client_data.id)

               print(f"\\n📊 {client_data.name}")
               print(f"   Health Score: {health['score']}/100")
               print(f"   Tickets (30d): {metrics['tickets_created']} created, {metrics['tickets_resolved']} resolved")

               # Flag clients needing attention
               if health['score'] < 70:
                   print(f"   ⚠️  Requires attention")
                   await client.clients.add_tag(client_data.id, "needs-attention")

Client Migration
^^^^^^^^^^^^^^^^

.. code-block:: python

   async def migrate_client_data(old_client_id: str, new_client_id: str):
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Export data from old client
           old_data = await client.clients.export_client_data(old_client_id)

           # Get tags from old client
           old_tags = await client.clients.get_tags(old_client_id)

           # Apply tags to new client
           for tag in old_tags:
               await client.clients.add_tag(new_client_id, tag)

           # Add migration tag
           await client.clients.add_tag(new_client_id, f"migrated-from-{old_client_id}")

           # Deactivate old client
           await client.clients.deactivate_client(old_client_id)

           print(f"Migration completed: {old_client_id} -> {new_client_id}")

Error Handling
--------------

The ClientManager includes comprehensive error handling:

.. code-block:: python

   from py_superops import (
       SuperOpsAPIError,
       SuperOpsResourceNotFoundError,
       SuperOpsValidationError
   )

   async def robust_client_operations():
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           try:
               # Attempt to get client
               client_data = await client.clients.get_by_email("nonexistent@example.com")

               if not client_data:
                   print("Client not found")
                   return

               # Attempt status update
               await client.clients.activate_client(client_data.id)

           except SuperOpsResourceNotFoundError:
               print("Client resource not found")
           except SuperOpsValidationError as e:
               print(f"Validation error: {e.message}")
           except SuperOpsAPIError as e:
               print(f"API error: {e.message} (status: {e.status_code})")

Best Practices
--------------

1. **Use Pagination**: Always use appropriate page sizes for large client lists
2. **Cache Client Data**: Cache frequently accessed client information
3. **Bulk Operations**: Use bulk methods for efficiency when updating multiple clients
4. **Tag Strategy**: Develop consistent tagging strategies for client organization
5. **Health Monitoring**: Regularly monitor client health scores
6. **Data Export**: Regularly export client data for backup purposes

Performance Tips
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Good: Use pagination for large datasets
   page = 1
   all_clients = []
   while True:
       batch = await client.clients.get_active_clients(page_size=100, page=page)
       all_clients.extend(batch['items'])
       if len(batch['items']) < 100:
           break
       page += 1

   # Good: Use bulk operations
   client_ids = [c.id for c in all_clients[:10]]
   await client.clients.bulk_add_tags(client_ids, ["bulk-update"])

   # Good: Cache frequently accessed data
   client_cache = {}

   async def get_cached_client(client_id: str):
       if client_id not in client_cache:
           client_cache[client_id] = await client.clients.get_by_id(client_id)
       return client_cache[client_id]

Related Managers
----------------

The ClientManager works closely with other managers:

- :doc:`contacts` - Managing client contacts
- :doc:`sites` - Managing client sites
- :doc:`tickets` - Client support tickets
- :doc:`assets` - Client assets and devices
- :doc:`projects` - Client projects

API Reference
-------------

For complete API details, see :class:`py_superops.managers.ClientManager`.

.. autoclass:: py_superops.managers.ClientManager
   :members:
   :inherited-members:
   :show-inheritance:
