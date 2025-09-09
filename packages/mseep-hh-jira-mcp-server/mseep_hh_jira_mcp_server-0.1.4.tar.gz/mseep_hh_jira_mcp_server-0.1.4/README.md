# hh-jira-mcp-server MCP server

A MCP server project

## Quickstart

Register at https://claude.ai and buy Pro subscription

### Install

Install Claude Desktop
https://claude.ai/download

Install uv:
```bash
brew install uv
```

Install keyring:
https://pypi.org/project/keyring/

#### Store password for jira account
```bash
keyring set hh-jira-mcp-server v.pupkin
```

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Published Servers Configuration
```json
{
  "mcpServers": {
    "hh-jira-mcp-server": {
      "command": "uvx",
      "args": [
        "hh-jira-mcp-server"
      ],
      "env": {
        "HH_JIRA_MCP_USER": "v.pupkin",
        "HH_JIRA_MCP_TEAM": "some-team",
        "HH_JIRA_MCP_SEARCH_FILTER": "status in (\"Development: In progress\")"
      }
    }
  }
}
```

Development/Unpublished Servers Configuration
```json
{
  "mcpServers": {
    "hh-jira-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "<path_to_project>/hh-jira-mcp-server",
        "run",
        "hh-jira-mcp-server"
      ],
      "env": {
        "HH_JIRA_MCP_USER": "v.pupkin",
        "HH_JIRA_MCP_TEAM": "some-team",
        "HH_JIRA_MCP_SEARCH_FILTER": "status in (\"Development: In progress\")"
      }
    }
  }
}
```

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory <path_to_project>/hh-jira-mcp-server run hh-jira-mcp-server
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.