# IP Geolocation MCP Server

This is a simple [Model Context Protocol](https://modelcontextprotocol.io) server that uses the [ipinfo.io](https://ipinfo.io) API to get detailed information about an IP address.
This can be used to determine where the user is located (approximately) and what network they are used.

<a href="https://glama.ai/mcp/servers/pll7u5ak1h">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/pll7u5ak1h/badge" alt="IP Geolocation Server MCP server" />
</a>

![Example conversation using mcp-server-ipinfo](demo.png)


## Installation

You'll need to create a token to use the IPInfo API.
If you don't already have one, you can sign up for a free account at https://ipinfo.io/signup.

While each client has its own way of specifying, you'll generally use the following values:

| Field | Value |
|-------|-------|
| **Command** | `uvx` |
| **Arguments** | `mcp-server-ipinfo` |
| **Environment** | `IPINFO_API_TOKEN` = `<YOUR TOKEN>` |


### Development Version

If you'd like to use the latest and greatest, the server can be pulled straight from GitHub.
Just add an additional `--from` argument:


| Field | Value |
|-------|-------|
| **Command** | `uvx` |
| **Arguments** | `--from`, `git+https://github.com/briandconnelly/mcp-server-ipinfo`, `mcp-server-ipinfo` |
| **Environment** | `IPINFO_API_TOKEN` = `<YOUR TOKEN>` |


## Components

### Tools

- `get_ip_details`: This tool is used to get detailed information about an IP address.
    - **Input:** `ip`: The IP address to get information about.
    - **Output:** `IPDetails`: A Pydantic model containing detailed information about the IP, including location, organization, and country details.

### Resources   

_No custom resources are included_

### Prompts

_No custom prompts are included_


## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with [IPInfo](https://ipinfo.io).
