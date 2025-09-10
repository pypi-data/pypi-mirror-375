# Gemini Bridge

![CI Status](https://github.com/eLyiN/gemini-bridge/actions/workflows/ci.yml/badge.svg)
![PyPI Version](https://img.shields.io/pypi/v/gemini-bridge)
![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)
![Gemini CLI](https://img.shields.io/badge/Gemini-CLI-blue.svg)

A lightweight MCP (Model Context Protocol) server that enables AI coding assistants to interact with Google's Gemini AI through the official CLI. Works with Claude Code, Cursor, VS Code, and other MCP-compatible clients. Designed for simplicity, reliability, and seamless integration.

## ✨ Features

- **Direct Gemini CLI Integration**: Zero API costs using official Gemini CLI
- **Simple MCP Tools**: Two core functions for basic queries and file analysis
- **Stateless Operation**: No sessions, caching, or complex state management
- **Production Ready**: Robust error handling with configurable 60-second timeouts
- **Minimal Dependencies**: Only requires `mcp>=1.0.0` and Gemini CLI
- **Easy Deployment**: Support for both uvx and traditional pip installation
- **Universal MCP Compatibility**: Works with any MCP-compatible AI coding assistant

## 🚀 Quick Start

### Prerequisites

1. **Install Gemini CLI**:
   ```bash
   npm install -g @google/gemini-cli
   ```

2. **Authenticate with Gemini**:
   ```bash
   gemini auth login
   ```

3. **Verify installation**:
   ```bash
   gemini --version
   ```

### Installation

**🎯 Recommended: PyPI Installation**
```bash
# Install from PyPI
pip install gemini-bridge

# Add to Claude Code with uvx (recommended)
claude mcp add gemini-bridge -s user -- uvx gemini-bridge
```

**Alternative: From Source**
```bash
# Clone the repository
git clone https://github.com/shelakh/gemini-bridge.git
cd gemini-bridge

# Build and install locally
uvx --from build pyproject-build
pip install dist/*.whl

# Add to Claude Code
claude mcp add gemini-bridge -s user -- uvx gemini-bridge
```

**Development Installation**
```bash
# Clone and install in development mode
git clone https://github.com/shelakh/gemini-bridge.git
cd gemini-bridge
pip install -e .

# Add to Claude Code (development)
claude mcp add gemini-bridge-dev -s user -- python -m src
```

## 🌐 Multi-Client Support

**Gemini Bridge works with any MCP-compatible AI coding assistant** - the same server supports multiple clients through different configuration methods.

### Supported MCP Clients
- **Claude Code** ✅ (Default)
- **Cursor** ✅
- **VS Code** ✅
- **Windsurf** ✅
- **Cline** ✅
- **Void** ✅
- **Cherry Studio** ✅
- **Augment** ✅
- **Roo Code** ✅
- **Zencoder** ✅
- **Any MCP-compatible client** ✅

### Configuration Examples

<details>
<summary><strong>Claude Code</strong> (Default)</summary>

```bash
# Recommended installation
claude mcp add gemini-bridge -s user -- uvx gemini-bridge

# Development installation
claude mcp add gemini-bridge-dev -s user -- python -m src
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

**Global Configuration** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

**Project-Specific** (`.cursor/mcp.json` in your project):
```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

Go to: `Settings` → `Cursor Settings` → `MCP` → `Add new global MCP server`

</details>

<details>
<summary><strong>VS Code</strong></summary>

**Configuration** (`.vscode/mcp.json` in your workspace):
```json
{
  "servers": {
    "gemini-bridge": {
      "type": "stdio",
      "command": "uvx",
      "args": ["gemini-bridge"]
    }
  }
}
```

**Alternative: Through Extensions**
1. Open Extensions view (Ctrl+Shift+X)
2. Search for MCP extensions
3. Add custom server with command: `uvx gemini-bridge`

</details>

<details>
<summary><strong>Windsurf</strong></summary>

Add to your Windsurf MCP configuration:
```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary><strong>Cline</strong> (VS Code Extension)</summary>

1. Open Cline and click **MCP Servers** in the top navigation
2. Select **Installed** tab → **Advanced MCP Settings**
3. Add to `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary><strong>Void</strong></summary>

Go to: `Settings` → `MCP` → `Add MCP Server`

```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary><strong>Cherry Studio</strong></summary>

1. Navigate to **Settings → MCP Servers → Add Server**
2. Fill in the server details:
   - **Name**: `gemini-bridge`
   - **Type**: `STDIO`
   - **Command**: `uvx`
   - **Arguments**: `["gemini-bridge"]`
3. Save the configuration

</details>

<details>
<summary><strong>Augment</strong></summary>

**Using the UI:**
1. Click hamburger menu → **Settings** → **Tools**
2. Click **+ Add MCP** button
3. Enter command: `uvx gemini-bridge`
4. Name: **Gemini Bridge**

**Manual Configuration:**
```json
"augment.advanced": { 
  "mcpServers": [ 
    { 
      "name": "gemini-bridge", 
      "command": "uvx", 
      "args": ["gemini-bridge"],
      "env": {}
    }
  ]
}
```

</details>

<details>
<summary><strong>Roo Code</strong></summary>

1. Go to **Settings → MCP Servers → Edit Global Config**
2. Add to `mcp_settings.json`:

```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary><strong>Zencoder</strong></summary>

1. Go to Zencoder menu (...) → **Tools** → **Add Custom MCP**
2. Add configuration:

```json
{
  "command": "uvx",
  "args": ["gemini-bridge"],
  "env": {}
}
```

3. Hit the **Install** button

</details>

<details>
<summary><strong>Alternative Installation Methods</strong></summary>

**For pip-based installations:**
```json
{
  "command": "gemini-bridge",
  "args": [],
  "env": {}
}
```

**For development/local testing:**
```json
{
  "command": "python",
  "args": ["-m", "src"],
  "env": {},
  "cwd": "/path/to/gemini-bridge"
}
```

**For npm-style installation** (if needed):
```json
{
  "command": "npx",
  "args": ["gemini-bridge"],
  "env": {}
}
```

</details>

### Universal Usage

Once configured with any client, use the same two tools:

1. **Ask general questions**: "What authentication patterns are used in this codebase?"
2. **Analyze specific files**: "Review these auth files for security issues"

**The server implementation is identical** - only the client configuration differs!

## ⚙️ Configuration

### Timeout Configuration

By default, Gemini Bridge uses a 60-second timeout for all CLI operations. For longer queries (large files, complex analysis), you can configure a custom timeout using the `GEMINI_BRIDGE_TIMEOUT` environment variable.

**Example configurations:**

<details>
<summary><strong>Claude Code</strong></summary>

```bash
# Add with custom timeout (120 seconds)
claude mcp add gemini-bridge -s user --env GEMINI_BRIDGE_TIMEOUT=120 -- uvx gemini-bridge
```

</details>

<details>
<summary><strong>Manual Configuration (mcp_settings.json)</strong></summary>

```json
{
  "mcpServers": {
    "gemini-bridge": {
      "command": "uvx",
      "args": ["gemini-bridge"],
      "env": {
        "GEMINI_BRIDGE_TIMEOUT": "120"
      }
    }
  }
}
```

</details>

**Timeout Options:**
- **Default**: 60 seconds (if not configured)
- **Range**: Any positive integer (seconds)
- **Recommended**: 120-300 seconds for large file analysis
- **Invalid values**: Fall back to 60 seconds with warning

## 🛠️ Available Tools

### `consult_gemini`
Direct CLI bridge for simple queries.

**Parameters:**
- `query` (string): The question or prompt to send to Gemini
- `directory` (string): Working directory for the query (default: current directory)
- `model` (string, optional): Model to use - "flash" or "pro" (default: "flash")

**Example:**
```python
consult_gemini(
    query="Find authentication patterns in this codebase",
    directory="/path/to/project",
    model="flash"
)
```

### `consult_gemini_with_files`
CLI bridge with file attachments for detailed analysis.

**Parameters:**
- `query` (string): The question or prompt to send to Gemini
- `directory` (string): Working directory for the query
- `files` (list): List of file paths relative to the directory
- `model` (string, optional): Model to use - "flash" or "pro" (default: "flash")

**Example:**
```python
consult_gemini_with_files(
    query="Analyze these auth files and suggest improvements",
    directory="/path/to/project",
    files=["src/auth.py", "src/models.py"],
    model="pro"
)
```

## 📋 Usage Examples

### Basic Code Analysis
```python
# Simple research query
consult_gemini(
    query="What authentication patterns are used in this project?",
    directory="/Users/dev/my-project"
)
```

### Detailed File Review
```python
# Analyze specific files
consult_gemini_with_files(
    query="Review these files and suggest security improvements",
    directory="/Users/dev/my-project",
    files=["src/auth.py", "src/middleware.py"],
    model="pro"
)
```

### Multi-file Analysis
```python
# Compare multiple implementation files
consult_gemini_with_files(
    query="Compare these database implementations and recommend the best approach",
    directory="/Users/dev/my-project",
    files=["src/db/postgres.py", "src/db/sqlite.py", "src/db/redis.py"]
)
```

## 🏗️ Architecture

### Core Design
- **CLI-First**: Direct subprocess calls to `gemini` command
- **Stateless**: Each tool call is independent with no session state
- **Fixed Timeout**: 60-second maximum execution time
- **Simple Error Handling**: Clear error messages with fail-fast approach

### Project Structure
```
gemini-bridge/
├── src/
│   ├── __init__.py              # Entry point
│   ├── __main__.py              # Module execution entry point
│   └── mcp_server.py            # Main MCP server implementation
├── .github/                     # GitHub templates and workflows
├── pyproject.toml              # Python package configuration
├── README.md                   # This file
├── CONTRIBUTING.md             # Contribution guidelines
├── CODE_OF_CONDUCT.md          # Community standards
├── SECURITY.md                 # Security policies
├── CHANGELOG.md               # Version history
└── LICENSE                    # MIT license
```

## 🔧 Development

### Local Testing
```bash
# Install in development mode
pip install -e .

# Run directly
python -m src

# Test CLI availability
gemini --version
```

### Integration with Claude Code
The server automatically integrates with Claude Code when properly configured through the MCP protocol.

## 🔍 Troubleshooting

### CLI Not Available
```bash
# Install Gemini CLI
npm install -g @google/gemini-cli

# Authenticate
gemini auth login

# Test
gemini --version
```

### Connection Issues
- Verify Gemini CLI is properly authenticated
- Check network connectivity
- Ensure Claude Code MCP configuration is correct
- Check that the `gemini` command is in your PATH

### Timeout Issues 🔥

Gemini Bridge now includes comprehensive timeout debugging. If you're experiencing timeout issues:

**1. Use the Debug Tool**
```python
# Get detailed diagnostics about your configuration
get_debug_info()
```

This will show:
- Current timeout configuration
- Gemini CLI status and version
- Authentication status
- Environment variables
- System information

**2. Configure Appropriate Timeout**

For different operation types, recommended timeouts:

- **Default operations**: 60 seconds (default)
- **Large file analysis**: 240 seconds
- **Complex multi-file operations**: 300+ seconds

**Configuration Examples:**

```bash
# Claude Code with 4-minute timeout for large operations
claude mcp add gemini-bridge -s user --env GEMINI_BRIDGE_TIMEOUT=240 -- uvx gemini-bridge

# Environment variable (if running manually)
export GEMINI_BRIDGE_TIMEOUT=240
```

**3. Common Timeout Scenarios**

| Scenario | Recommended Timeout | Reason |
|----------|-------------------|---------|
| Single file < 10KB | 60s (default) | Fast processing |
| Multiple files or large files | 240s | More content to process |
| Complex code analysis | 300s | Deep reasoning required |
| Very large files (>100KB) | 300-600s | Processing overhead |

**4. Debugging Steps**

1. **Check your configuration**:
   ```bash
   # Run the debug tool to see current timeout
   # Look for "Actual timeout used" in the output
   ```

2. **Monitor logs**: The server now logs detailed timing information

3. **Test with smaller queries**: If large queries timeout, break them into smaller parts

4. **Verify Gemini CLI performance**: Test `gemini` directly with similar queries

**5. Advanced Troubleshooting**

If timeouts persist even with high timeout values:

- **Network issues**: Check your internet connection
- **Gemini CLI version**: Update with `npm install -g @google/gemini-cli@latest`  
- **Authentication**: Re-authenticate with `gemini auth login`
- **System resources**: Check if your system is under high load
- **File encoding**: Ensure files are UTF-8 encoded
- **MCP client timeout**: Some clients have their own timeout settings

### Common Error Messages
- **"CLI not available"**: Gemini CLI is not installed or not in PATH
- **"Authentication required"**: Run `gemini auth login`
- **"Timeout after X seconds"**: Operation took longer than configured timeout
  - Solution: Increase `GEMINI_BRIDGE_TIMEOUT` environment variable
  - For immediate testing: Use smaller files or simpler queries
- **"Large content size warning"**: Files total >100KB, may need longer timeout
- **"Very high timeout configured"**: Timeout >300s, failed operations will wait long

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

### Quick Contributing Guide
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/shelakh/gemini-bridge/issues)
- **Discussions**: Join the community discussion
- **Documentation**: Additional docs can be created in the `docs/` directory

---

**Focus**: A simple, reliable bridge between Claude Code and Gemini AI through the official CLI.