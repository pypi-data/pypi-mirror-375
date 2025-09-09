To start the project

```bash
uv venv
```

```bash
uv sync
```

```bash
mcp dev server.py
```

After every change in the code, you need to re run

```bash
mcp dev server.py
```

NOTE: You should look into how to do hot reloads

Look into how the other example mcp servers are running with their respective tool exposing

Potential next steps:

- Should I expose API Keys and stuff as a resource or should i make the platform url as a resource
- one of the tools should be getting a new api_key and project_id for the user if they dont have it for the current one but I need to get the right user somehow
- Look into how the other tools are doing this stuff

Write mcp prompts that help llms understand how to write the prompts for best results

Servers to look at:

Looks lke most of these are using ts, maybe I should also change gears to that

Actually I dont see why typescript would be better especially in our usecase, so sticking to better readbility python might be better

- [Fetch](https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/src/mcp_server_fetch/server.py)

- [Brave Search](https://github.com/modelcontextprotocol/servers/blob/main/src/brave_search/src/mcp_server_brave_search/server.py)

- [Slack](https://github.com/modelcontextprotocol/servers/blob/main/src/slack/index.ts)

- [Puppeteer](https://github.com/modelcontextprotocol/servers/blob/main/src/puppeteer/index.ts)

- https://github.com/rileyedwards77/perplexity-mcp-server

# Potential Contributions

Hot reload when the developer writes code to MCP
