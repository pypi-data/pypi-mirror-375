# ai-search-adm

> **⚠️ PRERELEASE SOFTWARE**: This is beta software. Features may change and bugs may exist. Use with caution in production environments.

Administration tool for Azure AI Search indexes.

## Features

- **duplicate**: Duplicate an index definition (schema only, no documents)
- **clear**: Clear all documents from an index (preserves schema)
- **list**: List all indexes in a search service
- **stats**: Show index statistics (document count, storage usage)
- Uses `DefaultAzureCredential` for authentication (or API key as fallback)
- Pretty terminal output with Rich
- Cross-service index duplication support

## Installation

> **Note**: This is currently in beta. To install the beta version, you may need to use `--pre` flag with pip or specify the exact version.

### Using uvx (Recommended)
Run directly without installation:
```bash
uvx ai-search-adm --help
uvx ai-search-adm list --endpoint https://myservice.search.windows.net
```

Or install globally:
```bash
uvx install ai-search-adm
ai-search-adm --help
```

### Using uv
Install as a tool:
```bash
uv tool install ai-search-adm
ai-search-adm --help
```

Run without installation:
```bash
uv tool run ai-search-adm --help
uv tool run ai-search-adm list --endpoint https://myservice.search.windows.net
```

### Using pip (Traditional)
```bash
# For beta versions, use --pre flag
pip install --pre ai-search-adm

# Or specify exact version
pip install ai-search-adm==0.9.0b1

ai-search-adm --help
```

### Using pipx
```bash
pipx install ai-search-adm
ai-search-adm --help
```

**Note**: All methods work identically. `uvx` and `uv tool run` are fastest and avoid dependency conflicts by running in isolated environments.

## Usage

### List indexes

List all indexes in a search service:

```bash
ai-search-adm list --endpoint https://your-service.search.windows.net
```

### Clear an index

Remove all documents from an index while preserving its structure:

```bash
ai-search-adm clear \
  --endpoint https://your-service.search.windows.net \
  --index index-name
```

⚠️ **WARNING**: This is a destructive operation that cannot be undone. You will be prompted to type "DELETE" to confirm.

### Get index statistics

Display document count and storage usage for an index:

```bash
ai-search-adm stats \
  --endpoint https://your-service.search.windows.net \
  --index index-name
```

### Duplicate an index

Duplicate an index within the same search service:

```bash
ai-search-adm duplicate \
  --endpoint https://your-service.search.windows.net \
  --source source-index-name \
  --target new-index-name
```

Duplicate an index across different search services:

```bash
ai-search-adm duplicate \
  --endpoint https://target-service.search.windows.net \
  --from-endpoint https://source-service.search.windows.net \
  --source source-index-name \
  --target new-index-name
```

### Authentication

By default, the tool uses `DefaultAzureCredential` which supports:
- Environment variables (service principal)
- Managed Identity
- Azure CLI authentication
- Visual Studio Code authentication
- And more...

You can also use API keys:

```bash
ai-search-adm duplicate \
  --endpoint https://your-service.search.windows.net \
  --api-key your-admin-api-key \
  --source source-index \
  --target target-index
```

### Options

- `--overwrite`: Delete target index if it exists (DANGEROUS)
- `--api-key`: Use API key authentication instead of DefaultAzureCredential
- `--source-api-key`: Use different API key for source service in cross-service scenarios

## Requirements

- Python 3.11+
- Azure AI Search service
- Appropriate permissions (Search Service Contributor role or API keys)

## Development

This project uses modern Python packaging with `pyproject.toml` and supports Python 3.11+.

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/

# Lint code  
ruff check src/ tests/

# Type check
mypy src/
```