# py-superops Documentation

This directory contains the comprehensive Sphinx documentation for the py-superops project.

## Overview

The documentation is built using [Sphinx](https://www.sphinx-doc.org/) with the following key features:

- **Modern Theme**: Uses sphinx-rtd-theme for professional appearance
- **API Documentation**: Auto-generated from docstrings using autodoc
- **Type Hints**: Full type hint support with sphinx-autodoc-typehints
- **MyST Parser**: Support for both reStructuredText and Markdown
- **Comprehensive Coverage**: All managers, configuration, examples, and guides

## Documentation Structure

```
docs/
├── source/
│   ├── index.rst                    # Main documentation index
│   ├── getting-started/            # Getting started guides
│   │   ├── installation.rst
│   │   ├── quickstart.rst
│   │   ├── configuration.rst
│   │   └── authentication.rst
│   ├── guide/                      # User guides
│   │   ├── client-usage.rst
│   │   ├── managers-overview.rst
│   │   ├── error-handling.rst
│   │   ├── async-patterns.rst
│   │   ├── graphql-queries.rst
│   │   └── best-practices.rst
│   ├── managers/                   # Manager documentation
│   │   ├── clients.rst            # Comprehensive client manager docs
│   │   ├── tickets.rst
│   │   ├── assets.rst
│   │   └── ... (all 17 managers)
│   ├── examples/                   # Code examples
│   │   ├── basic-usage.rst
│   │   ├── ticket-workflows.rst
│   │   ├── asset-management.rst
│   │   └── advanced-patterns.rst
│   ├── api/                        # API reference
│   │   ├── client.rst             # SuperOpsClient reference
│   │   ├── config.rst             # Configuration reference
│   │   ├── managers.rst           # All managers reference
│   │   ├── exceptions.rst         # Exception hierarchy
│   │   ├── graphql.rst            # GraphQL utilities
│   │   └── auth.rst               # Authentication
│   ├── troubleshooting.rst
│   ├── changelog.rst
│   ├── contributing.rst
│   └── license.rst
├── build/                          # Generated documentation
├── Makefile                        # Build commands
└── make.bat                        # Windows build commands
```

## Building the Documentation

### Prerequisites

1. Install documentation dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

2. Activate your virtual environment:
   ```bash
   source venv/bin/activate  # On Linux/macOS
   # OR
   venv\Scripts\activate     # On Windows
   ```

### Build Commands

```bash
cd docs

# Build HTML documentation
make html

# Build and open in browser
make html && python -m http.server 8080 -d build/html

# Clean previous builds
make clean

# Build other formats
make latexpdf  # PDF via LaTeX
make epub      # EPUB format
make man       # Man pages
```

### Development Build

For development with auto-rebuild on changes:

```bash
pip install sphinx-autobuild
sphinx-autobuild source build/html --open-browser
```

## Key Documentation Features

### Auto-Generated API Documentation

The documentation automatically generates API reference from docstrings:

- **SuperOpsClient**: Complete client API with examples
- **All 17 Managers**: Comprehensive manager documentation
- **Configuration**: All configuration options
- **Exceptions**: Exception hierarchy with handling examples
- **GraphQL Utilities**: Query builders and type definitions

### Comprehensive Examples

- **Real-world Usage**: Practical examples for common use cases
- **Error Handling**: Comprehensive error handling patterns
- **Async Patterns**: Best practices for async programming
- **Manager Examples**: Detailed examples for each manager

### Cross-References

The documentation includes extensive cross-references:
- Links between related managers
- API reference links from guides
- Example code references
- External library documentation links

## Testing Documentation

Test that documentation examples work:

```bash
python3 test_docs.py
```

This script verifies:
- All imports work correctly
- Configuration examples are valid
- Client creation succeeds
- Manager access works
- Package info functions work

## Documentation Guidelines

### Writing Style

1. **Clear and Concise**: Use simple, direct language
2. **Examples First**: Show working code examples before explanation
3. **Progressive Complexity**: Start simple, build to advanced topics
4. **Consistent Structure**: Follow established patterns

### Code Examples

1. **Complete Examples**: Always show complete, runnable code
2. **Error Handling**: Include appropriate error handling
3. **Type Hints**: Use type hints in examples
4. **Real Scenarios**: Base examples on actual use cases

### API Documentation

1. **Docstring Format**: Use Google-style docstrings
2. **Type Information**: Include complete type information
3. **Examples in Docstrings**: Add examples to method docstrings
4. **Cross-References**: Link to related methods and classes

## Troubleshooting

### Common Build Issues

1. **Import Errors**: Ensure py-superops is installed in development mode:
   ```bash
   pip install -e .
   ```

2. **Missing Dependencies**: Install all documentation dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

3. **Path Issues**: Build from the docs directory:
   ```bash
   cd docs && make html
   ```

4. **Cache Issues**: Clean and rebuild:
   ```bash
   make clean && make html
   ```

### Warning Messages

- **Intersphinx warnings**: Safe to ignore, indicates external docs unavailable
- **Type hint warnings**: Usually indicate missing imports in docstrings
- **Autodoc warnings**: May indicate missing or renamed methods

## Contributing to Documentation

1. **Focus Areas**: The client manager documentation (`managers/clients.rst`) is comprehensive - use it as a template
2. **New Sections**: Add new sections to the appropriate toctree
3. **Examples**: Test all code examples with `test_docs.py`
4. **Build Testing**: Always build and verify before committing

## Deployment

The documentation can be deployed to various platforms:

- **Read the Docs**: Automatic builds from GitHub
- **GitHub Pages**: Static site deployment
- **Internal Hosting**: Self-hosted documentation server

Configuration for Read the Docs is in `.readthedocs.yml` (to be created).

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Sphinx RTD Theme](https://sphinx-rtd-theme.readthedocs.io/)
