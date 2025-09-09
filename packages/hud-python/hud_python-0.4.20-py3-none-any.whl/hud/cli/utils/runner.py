"""Run Docker images as MCP servers."""

from __future__ import annotations

import asyncio
import subprocess
import sys

from hud.utils.design import HUDDesign

from .logging import find_free_port
from .server import MCPServerManager, run_server_with_interactive


def run_stdio_server(image: str, docker_args: list[str], verbose: bool) -> None:
    """Run Docker image as stdio MCP server (direct passthrough)."""
    design = HUDDesign()  # Use stderr for stdio mode

    # Build docker command
    docker_cmd = ["docker", "run", "--rm", "-i", *docker_args, image]

    if verbose:
        design.info(f"🐳 Running: {' '.join(docker_cmd)}")

    # Run docker directly with stdio passthrough
    try:
        result = subprocess.run(docker_cmd, stdin=sys.stdin)  # noqa: S603
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        design.info("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        design.error(f"Error: {e}")
        sys.exit(1)


async def run_http_server(image: str, docker_args: list[str], port: int, verbose: bool) -> None:
    """Run Docker image as HTTP MCP server (proxy mode)."""
    design = HUDDesign()

    # Create server manager
    server_manager = MCPServerManager(image, docker_args)

    # Find available port
    actual_port = find_free_port(port)
    if actual_port is None:
        design.error(f"No available ports found starting from {port}")
        return

    if actual_port != port:
        design.warning(f"Port {port} in use, using port {actual_port} instead")

    # Clean up any existing container
    server_manager.cleanup_container()

    # Build docker command
    docker_cmd = server_manager.build_docker_command()

    # Create MCP config
    config = server_manager.create_mcp_config(docker_cmd)

    # Create proxy
    proxy = server_manager.create_proxy(config)

    # Show header
    design.info("")  # Empty line
    design.header("HUD MCP Server", icon="🌐")

    # Show configuration
    design.section_title("Server Information")
    design.info(f"Port: {actual_port}")
    design.info(f"URL: http://localhost:{actual_port}/mcp")
    design.info(f"Container: {server_manager.container_name}")
    design.info("")
    design.progress_message("Press Ctrl+C to stop")

    try:
        await server_manager.run_http_server(proxy, actual_port, verbose)
    except KeyboardInterrupt:
        design.info("\n👋 Shutting down...")
    finally:
        # Clean up container
        server_manager.cleanup_container()


async def run_http_server_interactive(
    image: str, docker_args: list[str], port: int, verbose: bool
) -> None:
    """Run Docker image as HTTP MCP server with interactive testing."""
    # Create server manager
    server_manager = MCPServerManager(image, docker_args)

    # Use the shared utility function
    await run_server_with_interactive(server_manager, port, verbose)


def run_mcp_server(
    image: str,
    docker_args: list[str],
    transport: str,
    port: int,
    verbose: bool,
    interactive: bool = False,
) -> None:
    """Run Docker image as MCP server with specified transport."""
    if transport == "stdio":
        if interactive:
            design = HUDDesign()
            design.error("Interactive mode requires HTTP transport")
            sys.exit(1)
        run_stdio_server(image, docker_args, verbose)
    elif transport == "http":
        if interactive:
            # Run in interactive mode
            asyncio.run(run_http_server_interactive(image, docker_args, port, verbose))
        else:
            try:
                asyncio.run(run_http_server(image, docker_args, port, verbose))
            except Exception as e:
                # Suppress the graceful shutdown errors
                if not any(
                    x in str(e)
                    for x in [
                        "timeout graceful shutdown exceeded",
                        "Cancel 0 running task(s)",
                        "Application shutdown complete",
                    ]
                ):
                    design = HUDDesign()
                    design.error(f"Unexpected error: {e}")
    else:
        design = HUDDesign()
        design.error(f"Unknown transport: {transport}")
        sys.exit(1)
