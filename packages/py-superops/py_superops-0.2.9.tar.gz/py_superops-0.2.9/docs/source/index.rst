py-superops: Python Client for SuperOps API
============================================

.. image:: https://img.shields.io/pypi/v/py-superops.svg
   :target: https://pypi.org/project/py-superops/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/py-superops.svg
   :target: https://pypi.org/project/py-superops/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/superops/py-superops.svg
   :target: https://github.com/superops/py-superops/blob/main/LICENSE
   :alt: License

Welcome to **py-superops**, a comprehensive Python client library for the SuperOps GraphQL API.
This library provides async/await support, type safety, comprehensive error handling, and intuitive
high-level managers for all SuperOps resources.

.. note::
   SuperOps is a comprehensive MSP (Managed Service Provider) platform that combines PSA (Professional Services Automation),
   RMM (Remote Monitoring & Management), and other essential business tools in one unified solution.

Key Features
------------

✨ **Modern Python**: Built with Python 3.8+ support and full async/await capabilities
🔒 **Type Safe**: Complete type hints and Pydantic models for all API interactions
🏗️ **High-Level Managers**: Intuitive, Pythonic interfaces for all SuperOps resources
⚡ **Performance**: Connection pooling, request caching, and efficient batch operations
🛡️ **Robust**: Comprehensive error handling, automatic retries, and rate limiting
📚 **Well Documented**: Extensive documentation with examples and best practices

Quick Example
-------------

.. code-block:: python

   import asyncio
   from py_superops import SuperOpsClient, SuperOpsConfig

   async def main():
       # Create configuration from environment variables
       config = SuperOpsConfig.from_env()

       async with SuperOpsClient(config) as client:
           # Test connection
           connection_info = await client.test_connection()
           print(f"Connected: {connection_info['connected']}")

           # Get active clients
           clients = await client.clients.get_active_clients(page_size=10)
           for client_data in clients['items']:
               print(f"Client: {client_data.name} ({client_data.email})")

           # Handle overdue tickets
           overdue_tickets = await client.tickets.get_overdue_tickets()
           for ticket in overdue_tickets['items']:
               await client.tickets.change_priority(ticket.id, "HIGH")

   asyncio.run(main())

Installation
------------

Install py-superops using pip:

.. code-block:: bash

   pip install py-superops

For development with all optional dependencies:

.. code-block:: bash

   pip install "py-superops[yaml,dev,docs,examples]"

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   getting-started/installation
   getting-started/quickstart
   getting-started/configuration
   getting-started/authentication

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   guide/client-usage
   guide/managers-overview
   guide/error-handling
   guide/async-patterns
   guide/graphql-queries
   guide/best-practices

.. toctree::
   :maxdepth: 2
   :caption: Manager Guides:

   managers/clients
   managers/tickets
   managers/tasks
   managers/assets
   managers/projects
   managers/contacts
   managers/sites
   managers/users
   managers/knowledge-base
   managers/contracts
   managers/time-entries
   managers/attachments
   managers/comments
   managers/webhooks
   managers/automation
   managers/monitoring
   managers/scripts

.. toctree::
   :maxdepth: 2
   :caption: Examples:

   examples/basic-usage
   examples/ticket-workflows
   examples/asset-management
   examples/project-management
   examples/automation-scripts
   examples/advanced-patterns

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/client
   api/config
   api/managers
   api/exceptions
   api/graphql
   api/auth

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources:

   troubleshooting
   changelog
   contributing
   license

Support and Community
---------------------

- **GitHub Repository**: https://github.com/superops/py-superops
- **Documentation**: https://py-superops.readthedocs.io
- **Issue Tracker**: https://github.com/superops/py-superops/issues
- **SuperOps Support**: https://support.superops.com

The py-superops library is developed and maintained by the SuperOps team with contributions
from the community. We welcome bug reports, feature requests, and contributions!

License
-------

This project is licensed under the MIT License - see the :doc:`license` page for details.

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
