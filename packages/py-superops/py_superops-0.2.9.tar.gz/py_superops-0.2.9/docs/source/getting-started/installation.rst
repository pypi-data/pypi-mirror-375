Installation
============

System Requirements
-------------------

**py-superops** requires Python 3.8 or higher. We recommend using the latest stable version of Python for the best performance and security updates.

.. note::
   While Python 3.8 is the minimum supported version, we recommend Python 3.10+ for optimal performance and the latest language features.

**Supported Platforms:**

- Linux (Ubuntu 18.04+, CentOS 7+, RHEL 7+, etc.)
- macOS 10.15+ (Catalina and newer)
- Windows 10/11
- Docker containers

Installing py-superops
----------------------

Basic Installation
^^^^^^^^^^^^^^^^^^

Install py-superops using pip:

.. code-block:: bash

   pip install py-superops

This installs the core library with all required dependencies:

- ``httpx`` - Modern async HTTP client
- ``pydantic`` - Data validation and settings management
- ``pydantic-settings`` - Settings management with pydantic

Installation with Optional Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For enhanced functionality, you can install optional dependency groups:

**YAML Support:**

.. code-block:: bash

   pip install "py-superops[yaml]"

Includes ``PyYAML`` for reading YAML configuration files.

**Development Dependencies:**

.. code-block:: bash

   pip install "py-superops[dev]"

Includes testing, linting, and development tools:

- ``pytest`` and plugins for testing
- ``black``, ``isort``, ``ruff`` for code formatting
- ``mypy`` for type checking
- ``pre-commit`` for git hooks
- Security scanning tools

**Documentation Dependencies:**

.. code-block:: bash

   pip install "py-superops[docs]"

Includes Sphinx and related tools for building documentation.

**All Dependencies:**

.. code-block:: bash

   pip install "py-superops[yaml,dev,docs,examples]"

Virtual Environment Setup
--------------------------

We strongly recommend using a virtual environment to avoid dependency conflicts:

Using venv (Python 3.3+)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Create virtual environment
   python -m venv superops-env

   # Activate virtual environment
   # On Linux/macOS:
   source superops-env/bin/activate

   # On Windows:
   superops-env\\Scripts\\activate

   # Install py-superops
   pip install py-superops

Using conda
^^^^^^^^^^^

.. code-block:: bash

   # Create conda environment
   conda create -n superops-env python=3.11

   # Activate environment
   conda activate superops-env

   # Install py-superops
   pip install py-superops

Using Poetry
^^^^^^^^^^^^

If you're using Poetry for dependency management:

.. code-block:: bash

   # Add to your pyproject.toml
   poetry add py-superops

   # Or with optional dependencies
   poetry add "py-superops[yaml]"

Development Installation
------------------------

For development, clone the repository and install in editable mode:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/superops/py-superops.git
   cd py-superops

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate

   # Install in editable mode with dev dependencies
   pip install -e ".[dev,docs,yaml]"

   # Install pre-commit hooks
   pre-commit install

Docker Installation
-------------------

You can also use py-superops in a Docker container:

**Basic Dockerfile:**

.. code-block:: dockerfile

   FROM python:3.11-slim

   # Install py-superops
   RUN pip install py-superops

   # Copy your application
   COPY . /app
   WORKDIR /app

   # Run your application
   CMD ["python", "your_script.py"]

**Using Docker Compose:**

.. code-block:: yaml

   # docker-compose.yml
   version: '3.8'
   services:
     superops-app:
       build: .
       environment:
         - SUPEROPS_API_KEY=your-api-key
       volumes:
         - ./your_app:/app

Verifying Installation
----------------------

After installation, verify that py-superops is working correctly:

.. code-block:: python

   import py_superops

   # Check version
   print(f"py-superops version: {py_superops.__version__}")

   # Check available features
   package_info = py_superops.get_package_info()
   print(f"Available features: {package_info['features']}")

You should see output similar to:

.. code-block:: text

   py-superops version: 0.1.0
   Available features: ['Async GraphQL client with connection pooling', 'Type-safe query and mutation builders', ...]

Troubleshooting Installation Issues
-----------------------------------

Common Issues and Solutions
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**SSL Certificate Errors:**

If you encounter SSL errors during installation:

.. code-block:: bash

   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org py-superops

**Permission Errors:**

Use ``--user`` flag to install in user directory:

.. code-block:: bash

   pip install --user py-superops

**Outdated pip:**

Update pip first:

.. code-block:: bash

   pip install --upgrade pip
   pip install py-superops

**Dependency Conflicts:**

Use a fresh virtual environment to avoid conflicts:

.. code-block:: bash

   python -m venv fresh-env
   source fresh-env/bin/activate
   pip install py-superops

Platform-Specific Notes
^^^^^^^^^^^^^^^^^^^^^^^^

**Windows:**

- Use PowerShell or Command Prompt
- Some antivirus software may interfere with installation
- Windows Defender may require exceptions for development tools

**macOS:**

- Install Command Line Tools: ``xcode-select --install``
- Consider using Homebrew for Python: ``brew install python@3.11``

**Linux:**

- Install Python development headers: ``sudo apt-get install python3-dev`` (Ubuntu/Debian)
- For RHEL/CentOS: ``sudo yum install python3-devel``

Getting Help
------------

If you encounter installation issues:

1. **Check the GitHub Issues**: https://github.com/superops/py-superops/issues
2. **Create a new issue** with:
   - Your operating system and version
   - Python version (``python --version``)
   - Full error message
   - Installation command used

3. **Community Support**: Join our community discussions for help from other users

Next Steps
----------

Once installed, proceed to the :doc:`quickstart` guide to start using py-superops!
