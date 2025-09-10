# Huoshui File Converter

A secure MCP (Model Context Protocol) server for document format conversion within a specified working directory.

## Features

- 🔒 **Sandbox Security**: All operations restricted to a configured working directory
- 📄 **Format Support**: Convert between Markdown, DOCX, HTML, PDF, and TXT
- 🚀 **MCP Integration**: Full MCP protocol support with prompts, resources, and tools
- ⚙️ **Flexible Configuration**: CLI arguments, environment variables, or current directory
- 🔍 **Smart Detection**: Intelligent file format detection by content analysis

## Quick Start

### Installation

Option 1: From MCP Registry (Recommended)

This server is available in the Model Context Protocol Registry. Install it using your MCP client.

mcp-name: io.github.huoshuiai42/huoshui-file-converter

Option 2: Using uvx

```bash
uvx huoshui-file-converter
```

Option 3: Using pip

```bash
pip install huoshui-file-converter
```

### Basic Usage

```bash
# Use current directory
uvx huoshui-file-converter

# Specify working directory (recommended)
uvx huoshui-file-converter --dir "/path/to/documents"

# Short form
uvx huoshui-file-converter -d "~/Documents"
```

### MCP Client Configuration

For Claude Desktop or other MCP clients:

```json
{
  "mcpServers": {
    "huoshui-converter": {
      "command": "uvx",
      "args": ["huoshui-file-converter", "--dir", "/Users/yourname/Documents"]
    }
  }
}
```

## Configuration Options

### Priority Order

1. **CLI Argument** (highest priority): `--dir` or `-d`
2. **Environment Variable**: `HUOSHUI_WORKING_DIR`
3. **Smart Default**: Documents folder if current directory is problematic
4. **Current Directory** (fallback)

### Examples

```bash
# CLI argument (best for MCP clients)
uvx huoshui-file-converter --dir "/project/docs"

# Environment variable
export HUOSHUI_WORKING_DIR="/project/docs"
uvx huoshui-file-converter

# Current directory fallback
cd /project/docs
uvx huoshui-file-converter
```

## Supported Conversions

| From     | To                        |
| -------- | ------------------------- |
| Markdown | DOCX, HTML, PDF           |
| DOCX     | Markdown, HTML, PDF       |
| HTML     | Markdown, DOCX, PDF       |
| TXT      | Markdown, DOCX, HTML, PDF |

## MCP Tools & Resources

### Tools

- `convert_document`: Convert files between formats
- `detect_format`: Intelligent format detection

### Resources

- `file_list`: Browse directory contents (optimized for large directories)
  - `limit`: Control number of files shown (default: 100)
  - `supported_only`: Show only convertible files
- `file_get`: Get detailed file information
- `conversion_capability_list`: List supported conversions

### Prompts

- `role_and_rules`: AI assistant behavior guidelines

## Performance Features

- **Fast Directory Listing**: Extension-based format detection for large directories
- **Smart File Limits**: Default 100-file limit prevents UI freezing
- **Large File Handling**: Files >50MB are marked and handled specially
- **Selective Display**: Option to show only supported file formats
- **Memory Efficient**: Avoids reading file contents during directory browsing

## Security Features

- **Path Validation**: Prevents directory traversal attacks
- **Working Directory Restriction**: All operations sandboxed to configured directory
- **Startup Validation**: Checks directory existence and permissions
- **Relative Path Enforcement**: Absolute paths are rejected

## Command Line Options

```bash
$ uvx huoshui-file-converter --help

usage: huoshui-file-converter [-h] [--dir PATH] [--version]

Huoshui Document Converter - MCP Server for file conversion within a working directory

options:
  -h, --help         show this help message and exit
  --dir PATH, -d PATH
                     Working directory for file operations (default: current directory or HUOSHUI_WORKING_DIR env var)
  --version, -v      show program's version number and exit

Examples:
  uvx huoshui-file-converter                    # Use current directory
  uvx huoshui-file-converter --dir /docs        # Use specific directory
  uvx huoshui-file-converter -d ./project       # Use relative directory

Configuration Priority:
  1. CLI argument (--dir/-d)
  2. Environment variable (HUOSHUI_WORKING_DIR)
  3. Current working directory
```

## Error Handling

The server validates the working directory on startup:

```
✅ Working directory configured: /Users/name/Documents
📂 Source: CLI argument
```

Common errors and solutions:

| Error                | Solution                            |
| -------------------- | ----------------------------------- |
| Directory not found  | Create directory or fix path        |
| No write access      | Check permissions (`chmod` on Unix) |
| Path outside sandbox | Use relative paths only             |

## Development

### Requirements

- Python 3.8+
- pypandoc
- pandoc (system dependency)
- LaTeX (for PDF conversion)

### Testing

```bash
# Test configuration
uvx huoshui-file-converter --dir "/tmp/test"

# Check startup messages
# ✅ Working directory configured: /tmp/test
# 📂 Source: CLI argument
```

## Documentation

- [Working Directory Configuration](docs/working_directory_config.md)
- [MCP Configuration Examples](docs/mcp_configuration_examples.md)
- [Performance Optimization Guide](docs/performance_optimization.md)

## License

[Your license here]
