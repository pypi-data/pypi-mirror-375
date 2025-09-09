import sys
import yaml
import argparse
from fastmcp import FastMCP
from umleitung.mcp_config_ext import MCPConfig
import asyncio


def load_config(config_path: str) -> MCPConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    return MCPConfig.model_validate(raw)


async def build_proxy_server(
    config: MCPConfig,
    proxy_name: str,
    server_name: str,
) -> FastMCP:
    """
    Build and configure an Umleitung FastMCP proxy server (without running it).
    Returns a FastMCP instance ready for in-memory testing or live use.
    """
    proxy = FastMCP.as_proxy(config, name=proxy_name)
    umleitung_server = FastMCP(server_name)

    # Build prefix-aware whitelists
    allowed_full_names = set()
    mcp_servers = getattr(config, "mcpServers", {})
    all_available_tools = await proxy.get_tools()
    
    for sub_server_name, server_cfg in mcp_servers.items():
        allowed = getattr(server_cfg, "allowed_tools", None)
        blocked = getattr(server_cfg, "blocked_tools", None)

        # Find all tools that belong to this sub_server
        if len(mcp_servers.keys()) == 1:
            # Only one proxied server: tool names are bare ("foo")
            server_tools = set(all_available_tools.keys())
        else:
            # Multiple proxied servers: tool names are "prefix_tool"
            server_tools = {
                name
                for name in all_available_tools
                if name.startswith(f"{sub_server_name}_")
            }

        if allowed is not None:
            # Only those listed in allowed_tools
            if len(mcp_servers.keys()) == 1:
                allowed_full_names.update(allowed)
            else:
                allowed_full_names.update(
                    {f"{sub_server_name}_{cmd}" for cmd in allowed}
                )
        elif blocked is not None:
            # All except those in blocked_tools
            if len(mcp_servers.keys()) == 1:
                filtered = [name for name in server_tools if name not in blocked]
            else:
                filtered = [
                    name
                    for name in server_tools
                    if name.split(f"{sub_server_name}_", 1)[-1] not in blocked
                ]
            allowed_full_names.update(filtered)
        else:
            # No allowed/blocked tools: add all tools for this server
            allowed_full_names.update(server_tools)

    for allowed_name in allowed_full_names:
        tool = await proxy.get_tool(allowed_name)
        umleitung_server.add_tool(tool.copy())
    
    return umleitung_server


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Umleitung MCP Proxy Server")
    parser.add_argument(
        "config",
        nargs="?",
        default="proxy_config.yaml",
        help="Path to proxy configuration YAML file (default: proxy_config.yaml)"
    )
    parser.add_argument(
        "--transport",
        default="streamable-http",
        help="Transport type for the server (default: streamable-http)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--show-banner",
        action="store_true",
        default=True,
        help="Show FastMCP startup banner (default: True)"
    )
    parser.add_argument(
        "--no-show-banner",
        action="store_false",
        dest="show_banner",
        help="Hide FastMCP startup banner"
    )
    parser.add_argument(
        "--proxy-name",
        default="Composite Proxy",
        help="Name for the proxy server (default: Composite Proxy)"
    )
    parser.add_argument(
        "--server-name",
        default="Umleitung",
        help="Name for the Umleitung server (default: Umleitung)"
    )
    return parser.parse_args()


async def main(
    config_path: str,
    transport: str,
    host: str,
    port: int,
    show_banner: bool,
    proxy_name: str,
    server_name: str,
):
    config = load_config(config_path)
    proxy_server = await build_proxy_server(config, proxy_name=proxy_name, server_name=server_name)
    await proxy_server.run_async(transport=transport, host=host, port=port, show_banner=show_banner)


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        main(
            args.config,
            args.transport,
            args.host,
            args.port,
            args.show_banner,
            args.proxy_name,
            args.server_name,
        )
    )
