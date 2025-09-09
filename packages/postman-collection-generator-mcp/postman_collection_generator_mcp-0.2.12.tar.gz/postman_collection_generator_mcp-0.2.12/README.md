# Postman Collection Generator MCP Server

An MCP (Model Context Protocol) server that automatically generates Postman collections from API codebases. Supports multiple frameworks including FastAPI, Spring Boot, Flask, Express, and any codebase with OpenAPI/Swagger specifications.

## Features

- 🚀 **Multi-Framework Support**: FastAPI, Spring Boot, Flask, Express, NestJS
- 📋 **OpenAPI/Swagger First**: Automatically detects and uses OpenAPI specs when available
- 🔍 **Smart Code Analysis**: Falls back to AST/pattern matching when no spec is found
- 🔐 **Authentication Support**: Handles Bearer, Basic, and API Key authentication
- 📁 **Organized Output**: Groups endpoints by tags or path segments
- 🎯 **Accurate Detection**: Extracts request bodies, parameters, and response examples

## Installation

### For End Users (via uvx)

The easiest way to use this MCP server is with `uvx`:

```bash
# Install and run directly
uvx postman-collection-generator-mcp

# Or install globally
uv tool install postman-collection-generator-mcp
```

### For Development

```bash
# Clone the repository
git clone https://github.com/yourusername/postman-collection-generator-mcp.git
cd postman-collection-generator-mcp

# Install dependencies with Poetry
poetry install

# Run in development
poetry run postman-collection-generator-mcp
```

## Configuration

### Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

**For uvx installation (recommended):**
```json
{
  "mcpServers": {
    "postman-generator": {
      "command": "uvx",
      "args": ["--no-cache", "postman-collection-generator-mcp"],
      "env": {
        "BITBUCKET_EMAIL": "your-username",
        "BITBUCKET_API_TOKEN": "your-app-password",
        "output_directory": "/path/to/output"
      }
    }
  }
}
```

**For local development:**
```json
{
  "mcpServers": {
    "postman-generator": {
      "command": "poetry",
      "args": ["run", "postman-collection-generator-mcp"],
      "cwd": "/path/to/postman-collection-generator-mcp",
      "env": {
        "BITBUCKET_EMAIL": "your-username",
        "BITBUCKET_API_TOKEN": "your-app-password",
        "output_directory": "/path/to/output"
      }
    }
  }
}
```

### Environment Variables

- `BITBUCKET_EMAIL`: Your Bitbucket username (not email)
- `BITBUCKET_API_TOKEN`: Bitbucket app password with repository read access
- `GITHUB_TOKEN`: GitHub personal access token (for private repos)
- `output_directory`: Where to save generated Postman collections (default: current directory)

## Usage

Once configured, you can use the following commands in Claude:

```
Generate a Postman collection from https://github.com/username/repo.git

Create Postman collection for https://bitbucket.org/team/api-project.git
```

The server will:
1. Clone the repository
2. Detect the framework and analyze the codebase
3. Extract all API endpoints with their parameters and examples
4. Generate a Postman v2.1 collection file
5. Save it to your output directory

## Supported Frameworks

### With Full Support
- **FastAPI** (Python) - Full OpenAPI integration
- **Spring Boot** (Java) - Annotation-based detection
- **Express** (Node.js) - Route pattern matching
- **Flask** (Python) - Decorator-based detection
- **Django REST** (Python) - ViewSet and path detection

### Coming Soon
- NestJS (TypeScript)
- Ruby on Rails
- ASP.NET Core

## Publishing Updates to PyPI

### One-Time Setup
```bash
# Configure PyPI token (get from https://pypi.org/manage/account/token/)
poetry config pypi-token.pypi YOUR-PYPI-TOKEN
```

### Publishing Updates Workflow

1. **Update Version**
   ```bash
   # Update version in pyproject.toml
   poetry version patch  # for bug fixes (0.1.0 -> 0.1.1)
   poetry version minor  # for new features (0.1.0 -> 0.2.0)
   poetry version major  # for breaking changes (0.1.0 -> 1.0.0)
   ```

2. **Build Package**
   ```bash
   poetry build
   ```

3. **Publish to PyPI**
   ```bash
   poetry publish
   ```

4. **Test Installation**
   ```bash
   # Test the published package
   uvx --reinstall postman-collection-generator-mcp
   ```

### Automated Version Workflow
```bash
# Complete update workflow
poetry version patch && poetry build && poetry publish
```

### Users Update with uvx
After publishing, users can update with:
```bash
uvx --reinstall postman-collection-generator-mcp
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Quality
```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .
```

### Local Testing with MCP Inspector

#### Option 1: Test Published Version
```bash
# Set environment variables
export BITBUCKET_EMAIL="your-username"
export BITBUCKET_API_TOKEN="your-app-password"
export output_directory="/tmp/postman-test"

# Run published version in HTTP mode
uvx postman-collection-generator-mcp@latest --transport http --port 8000

# Connect MCP Inspector to: http://localhost:8000/mcp
```

#### Option 2: Test Development Version
```bash
# From project directory
cd /path/to/postman-collection-generator-mcp

# Set environment variables
export BITBUCKET_EMAIL="your-username"
export BITBUCKET_API_TOKEN="your-app-password"
export output_directory="/tmp/postman-test"

# Run development version in HTTP mode
poetry run postman-collection-generator-mcp --transport http --port 8000

# Connect MCP Inspector to: http://localhost:8000/mcp
```

#### Using the Test Scripts

**Interactive MCP Inspector Testing:**
```bash
# Basic usage
./test_mcp_inspector.sh

# Test specific version
./test_mcp_inspector.sh --version 0.1.3

# Test latest version
./test_mcp_inspector.sh --latest
```

**Automated HTTP API Testing:**
```bash
# Test with default repository
./scripts/test_http_api.sh

# Test with custom repository
./scripts/test_http_api.sh "https://github.com/user/repo.git"
```

#### Testing with MCP Inspector
1. Open [MCP Inspector](https://inspector.mcphub.com/) or run locally
2. Enter URL: `http://localhost:8000/mcp`
3. Click Connect
4. Test tools:
   - `generate_collection` with: `{"repo_url": "https://bitbucket.org/tymerepos/tb-payshap-svc.git"}`
   - `get_server_info` with: `{}`

## Architecture

The server follows clean architecture principles:

- **Models**: Pydantic models for API endpoints and Postman collections
- **Analyzers**: Framework-specific endpoint extraction logic
- **Generators**: Postman collection generation from API models
- **Clients**: Git repository access with authentication support

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Inspired by API development workflows and the need for automation