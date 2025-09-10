# Ki AWS Strands AgentCore MCP Server

MCP server for automating Strands Agent development and Bedrock AgentCore deployment workflow.

## Installation

```bash
uvx ki-aws-strands-agentcore-mcp-server@latest
```

## Usage

Add to your Q CLI Agent configuration:

```json
{
  "mcpServers": {
    "ki.aws.strands-agentcore-mcp-server": {
      "command": "uvx",
      "args": ["ki-aws-strands-agentcore-mcp-server@latest"]
    }
  }
}
```

## Tools

- `develop_strands_agent`: Phase 1 - Strands Agent development and local testing
- `deploy_to_agentcore`: Phase 2 - Bedrock AgentCore deployment

## Features

- Automatic virtual environment setup
- Package installation on startup
- Phase 1-2 workflow automation
- Compatible with Q CLI Agent
