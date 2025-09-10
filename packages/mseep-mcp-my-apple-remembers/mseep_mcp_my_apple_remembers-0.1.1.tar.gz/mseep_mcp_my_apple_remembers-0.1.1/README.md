# MCP Server - My Apple Remembers
**A simple MCP server that recalls and saves memories from and to Apple Notes.**

[![Docker Pulls](https://img.shields.io/docker/pulls/buryhuang/mcp-my-apple-remembers)](https://hub.docker.com/r/buryhuang/mcp-my-apple-remembers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<img width="600" alt="image" src="https://github.com/user-attachments/assets/9bd5bc1c-02fe-4e71-88c4-46b3e9438ac0" />


## Features

* **Memory Recall**: Access notes, calendar events, messages, files and other information from your Mac
* **Memory Persistence**: Save important information to Apple Notes for future reference
* **Minimal Setup**: Just enable Remote Login on the target Mac
* **Universal Compatibility**: Works with all macOS versions

## Control in your hand
You can use prompt to instruct how you want your memory to be save. For example:
```
You should always use Folder "baryhuang" on recall and save memory.
```

## Installation
- [Enable SSH on macOS](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac)
- [Install Docker Desktop for local Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
- [Add this MCP server to Claude Desktop](https://modelcontextprotocol.io/quickstart/user)

You can configure Claude Desktop to use the Docker image by adding the following to your Claude configuration:
```json
{
  "mcpServers": {
    "my-apple-remembers": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e",
        "MACOS_USERNAME=your_macos_username",
        "-e",
        "MACOS_PASSWORD=your_macos_password",
        "-e",
        "MACOS_HOST=localhost",
        "--rm",
        "buryhuang/mcp-my-apple-remembers:latest"
      ]
    }
  }
}
```

## Developer Instructions
### Clone the repo
```bash
# Clone the repository
git clone https://github.com/baryhuang/mcp-my-apple-remembers.git
cd mcp-my-apple-remembers
```

### Building the Docker Image

```bash
# Build the Docker image
docker build -t mcp-my-apple-remembers .
```

### Publishing Multi-Platform Docker Images

```bash
# Set up Docker buildx for multi-platform builds
docker buildx create --use

# Build and push the multi-platform image
docker buildx build --platform linux/amd64,linux/arm64 -t buryhuang/mcp-my-apple-remembers:latest --push .
```

### Tools Specifications

#### my_apple_recall_memory
Run AppleScript commands on a remote macOS system to recall memories. This tool helps access Apple Notes, Calendar events, iMessages, chat history, files, and other information on your Mac.

#### my_apple_save_memory
Run AppleScript commands on a remote macOS system to save important information. This tool allows AI to persist relevant information to Apple Notes for future reference. 

All tools require macOS SSH access, with host and password.

## Security Note

Always use secure, authenticated connections when accessing remote macOS machines. This tool should only be used with servers you trust and have permission to access.

## License

See the LICENSE file for details. 
