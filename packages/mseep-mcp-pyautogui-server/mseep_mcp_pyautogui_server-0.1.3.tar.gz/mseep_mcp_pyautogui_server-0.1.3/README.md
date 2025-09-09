# mcp-pyautogui-server

[![smithery badge](https://smithery.ai/badge/@hetaoBackend/mcp-pyautogui-server)](https://smithery.ai/server/@hetaoBackend/mcp-pyautogui-server)

A MCP (Model Context Protocol) server that provides automated GUI testing and control capabilities through PyAutoGUI.

## Features

* Control mouse movements and clicks
* Simulate keyboard input
* Take screenshots
* Find images on screen
* Get screen information
* Cross-platform support (Windows, macOS, Linux)

## Tools

The server implements the following tools:

### Mouse Control
* Move mouse to specific coordinates
* Click at current or specified position
* Drag and drop operations
* Get current mouse position

### Keyboard Control  
* Type text
* Press individual keys
* Hotkey combinations

### Screen Operations
* Take screenshots
* Get screen size
* Find image locations on screen
* Get pixel colors

## Installation

### Prerequisites

* Python 3.12+
* PyAutoGUI
* Other dependencies will be installed automatically

### Install Steps

Install the package:

```bash
pip install mcp-pyautogui-server
```

### Claude Desktop Configuration

On MacOS:
```bash
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

On Windows:
```bash
%APPDATA%/Claude/claude_desktop_config.json
```

Development/Unpublished Servers Configuration:
```json
{
  "mcpServers": {
    "mcp-pyautogui-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-pyautogui-server",
        "run",
        "mcp-pyautogui-server"
      ]
    }
  }
}
```

Published Servers Configuration:
```json
{
  "mcpServers": {
    "mcp-pyautogui-server": {
      "command": "uvx",
      "args": [
        "mcp-pyautogui-server"
      ]
    }
  }
}
```

## Development

### Building and Publishing

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

Note: Set PyPI credentials via environment variables or command flags:
* Token: `--token` or `UV_PUBLISH_TOKEN`
* Username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

For the best debugging experience, use the MCP Inspector.

Launch the MCP Inspector via npm:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-pyautogui-server run mcp-pyautogui-server
```

The Inspector will display a URL that you can access in your browser to begin debugging.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
