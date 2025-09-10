# Ki AWS Bedrock AgentCore Deployment MCP Server

MCP server for automating Bedrock AgentCore deployment workflow.

## Installation

```bash
uvx ki.aws-bedrock-agentcore-deployment-mcp-server@latest
```

## Usage

Add to your Q CLI Agent configuration:

```json
{
  "mcpServers": {
    "ki.aws-bedrock-agentcore-deployment-mcp-server": {
      "command": "uvx",
      "args": ["ki.aws-bedrock-agentcore-deployment-mcp-server@latest"]
    }
  }
}
```

## Tools

- `run_local_test`: Local testing execution
- `setup_agentcore_env`: AgentCore environment preparation
- `run_agentcore_deploy`: AgentCore deployment execution

## Features

- Automatic virtual environment setup
- Package installation on startup
- AgentCore deployment automation
- Compatible with Q CLI Agent
