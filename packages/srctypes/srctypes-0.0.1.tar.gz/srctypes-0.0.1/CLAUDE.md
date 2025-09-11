# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**srctypes** is a Python library providing type annotations for source code languages and file formats using `typing.Annotated`. The project creates typed aliases for programming languages, data formats, and web technologies.

## Technology Stack

- **Language**: Python 3.10 (fixed version in .python-version)
- **Package Manager**: UV (modern Python package manager)
- **Build System**: Hatchling (Python build backend)
- **Type System**: Python typing with `typing.Annotated`
- **Build Automation**: Just (command runner)

## Key Development Commands

The project uses a `justfile` for command automation. Key commands:

```bash
just                    # List all available commands
just build              # Build package using UV
just test               # Test package installation and imports
just dev-setup          # Install development dependencies
just fmt                # Format code (placeholder - not configured)
just lint               # Run linters (placeholder - not configured)
just publish            # Publish to PyPI
just release [patch|minor|major]  # Complete release workflow
```

## Architecture

### Type Annotation Pattern
All types are built on a base `source_code` type: `Annotated[str, "source_code"]`. Each module exports specific type aliases for its domain:

- `css.py`: CSS-related types (css, scss, sass, less, stylus)
- `js.py`: JavaScript-related types (js, jsx, coffee)
- `sql.py`: SQL dialect types (mysql, pgsql, sqlite, mssql, oracle, plsql, sql)
- `ts.py`: TypeScript-related types (ts, tsx, dts)
- `data.py`: Data format types (json, yaml, toml, ini, xml, csv, tsv)
- `web.py`: Web template types (html, django, jinja, hbs, mustache, pug, haml, slim, ejs)

### Main Module Structure
The `__init__.py` imports and re-exports all types from individual modules, plus common programming language types. This provides a single import point for all type annotations.

## Development Environment

### Package Management
- Uses UV as the primary package manager
- Dependencies defined in `pyproject.toml`
- Lock file: `uv.lock`
- Python version fixed to 3.10

### Environment Configuration
- Environment variables managed via `.env` file (template in `.env.example`)
- Required for PyPI publishing (API tokens)

## Current Limitations

**Testing Infrastructure**: Minimal testing - only basic smoke test via `just test` that verifies imports work. No unit tests or integration tests.

**Code Quality Tools**: Formatters and linters are configured as placeholders in justfile but not implemented.

**CI/CD**: No automated testing or publishing pipeline configured.

## Important Files

- `pyproject.toml` - Project metadata and build configuration
- `justfile` - Build automation and development commands
- `src/srctypes/__init__.py` - Main type exports and module structure
- `.env.example` - Environment configuration template

## Publishing

The project is configured for PyPI publishing using UV. Requires environment variables from `.env` file for API tokens.

## Type System Dependencies

Requires `typing-extensions>=4.1.1` for backwards compatibility with older Python versions.