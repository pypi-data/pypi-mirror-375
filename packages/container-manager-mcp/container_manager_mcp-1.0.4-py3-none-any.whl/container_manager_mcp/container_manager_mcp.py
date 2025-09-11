#!/usr/bin/env python
# coding: utf-8

import argparse
import os
import sys
import logging
from typing import Optional, List, Dict

from fastmcp import FastMCP, Context
from pydantic import Field
from container_manager_mcp.container_manager import create_manager


def setup_logging(
    is_mcp_server: bool = False, log_file: str = "container_manager_mcp.log"
):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"MCP server logging initialized to {log_file}")


mcp = FastMCP(name="ContainerManagerServer")


def to_boolean(string):
    normalized = str(string).strip().lower()
    true_values = {"t", "true", "y", "yes", "1"}
    false_values = {"f", "false", "n", "no", "0"}
    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert '{string}' to boolean")


def parse_image_string(image: str, default_tag: str = "latest") -> tuple[str, str]:
    """
    Parse a container image string into image and tag components.

    Args:
        image: Input image string (e.g., 'registry.arpa/ubuntu/ubuntu:latest' or 'nginx')
        default_tag: Fallback tag if none is specified (default: 'latest')

    Returns:
        Tuple of (image, tag) where image includes registry/repository, tag is the tag or default_tag
    """
    # Split on the last ':' to separate image and tag
    if ":" in image:
        parts = image.rsplit(":", 1)
        image_name, tag = parts[0], parts[1]
        # Ensure tag is valid (not a port or malformed)
        if "/" in tag or not tag:
            # If tag contains '/' or is empty, assume no tag was provided
            return image, default_tag
        return image_name, tag
    return image, default_tag


environment_silent = os.environ.get("SILENT", False)
environment_log_file = os.environ.get("LOG_FILE", None)
environment_container_manager_type = os.environ.get("CONTAINER_MANAGER_TYPE", None)

if environment_silent:
    environment_silent = to_boolean(environment_silent)

# Common tools


@mcp.tool(
    annotations={
        "title": "Get Version",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def get_version(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Getting version for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.get_version()
    except Exception as e:
        logger.error(f"Failed to get version: {str(e)}")
        raise RuntimeError(f"Failed to get version: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Get Info",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def get_info(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Getting info for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.get_info()
    except Exception as e:
        logger.error(f"Failed to get info: {str(e)}")
        raise RuntimeError(f"Failed to get info: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Images",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def list_images(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> List[Dict]:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing images for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_images()
    except Exception as e:
        logger.error(f"Failed to list images: {str(e)}")
        raise RuntimeError(f"Failed to list images: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Pull Image",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def pull_image(
    image: str = Field(
        description="Image name to pull (e.g., nginx, registry.arpa/ubuntu/ubuntu:latest)."
    ),
    tag: str = Field(
        description="Image tag (overridden if tag is included in image string)",
        default="latest",
    ),
    platform: Optional[str] = Field(
        description="Platform (e.g., linux/amd64)", default=None
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    # Parse image string to separate image and tag
    parsed_image, parsed_tag = parse_image_string(image, tag)
    logger.debug(
        f"Pulling image {parsed_image}:{parsed_tag} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.pull_image(parsed_image, parsed_tag, platform)
    except Exception as e:
        logger.error(f"Failed to pull image: {str(e)}")
        raise RuntimeError(f"Failed to pull image: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Remove Image",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def remove_image(
    image: str = Field(description="Image name or ID to remove"),
    force: bool = Field(description="Force removal", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Removing image {image} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.remove_image(image, force)
    except Exception as e:
        logger.error(f"Failed to remove image: {str(e)}")
        raise RuntimeError(f"Failed to remove image: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Prune Images",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def prune_images(
    all: bool = Field(description="Prune all unused images", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Pruning images for {manager_type}, all: {all}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.prune_images(all=all)
    except Exception as e:
        logger.error(f"Failed to prune images: {str(e)}")
        raise RuntimeError(f"Failed to prune images: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Containers",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def list_containers(
    all: bool = Field(
        description="Show all containers (default running only)", default=False
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> List[Dict]:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing containers for {manager_type}, all: {all}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_containers(all)
    except Exception as e:
        logger.error(f"Failed to list containers: {str(e)}")
        raise RuntimeError(f"Failed to list containers: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Run Container",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def run_container(
    image: str = Field(description="Image to run"),
    name: Optional[str] = Field(description="Container name", default=None),
    command: Optional[str] = Field(
        description="Command to run in container", default=None
    ),
    detach: bool = Field(description="Run in detached mode", default=False),
    ports: Optional[Dict[str, str]] = Field(
        description="Port mappings {container_port: host_port}", default=None
    ),
    volumes: Optional[Dict[str, Dict]] = Field(
        description="Volume mappings {/host/path: {bind: /container/path, mode: rw}}",
        default=None,
    ),
    environment: Optional[Dict[str, str]] = Field(
        description="Environment variables", default=None
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Running container from {image} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.run_container(
            image, name, command, detach, ports, volumes, environment
        )
    except Exception as e:
        logger.error(f"Failed to run container: {str(e)}")
        raise RuntimeError(f"Failed to run container: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Stop Container",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def stop_container(
    container_id: str = Field(description="Container ID or name"),
    timeout: int = Field(description="Timeout in seconds", default=10),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Stopping container {container_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.stop_container(container_id, timeout)
    except Exception as e:
        logger.error(f"Failed to stop container: {str(e)}")
        raise RuntimeError(f"Failed to stop container: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Remove Container",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def remove_container(
    container_id: str = Field(description="Container ID or name"),
    force: bool = Field(description="Force removal", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Removing container {container_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.remove_container(container_id, force)
    except Exception as e:
        logger.error(f"Failed to remove container: {str(e)}")
        raise RuntimeError(f"Failed to remove container: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Prune Containers",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def prune_containers(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Pruning containers for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.prune_containers()
    except Exception as e:
        logger.error(f"Failed to prune containers: {str(e)}")
        raise RuntimeError(f"Failed to prune containers: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Get Container Logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def get_container_logs(
    container_id: str = Field(description="Container ID or name"),
    tail: str = Field(
        description="Number of lines to show from the end (or 'all')", default="all"
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> str:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Getting logs for container {container_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.get_container_logs(container_id, tail)
    except Exception as e:
        logger.error(f"Failed to get container logs: {str(e)}")
        raise RuntimeError(f"Failed to get container logs: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Exec in Container",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def exec_in_container(
    container_id: str = Field(description="Container ID or name"),
    command: List[str] = Field(description="Command to execute"),
    detach: bool = Field(description="Detach execution", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Executing {command} in container {container_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.exec_in_container(container_id, command, detach)
    except Exception as e:
        logger.error(f"Failed to exec in container: {str(e)}")
        raise RuntimeError(f"Failed to exec in container: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Volumes",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def list_volumes(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing volumes for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_volumes()
    except Exception as e:
        logger.error(f"Failed to list volumes: {str(e)}")
        raise RuntimeError(f"Failed to list volumes: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Create Volume",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def create_volume(
    name: str = Field(description="Volume name"),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Creating volume {name} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.create_volume(name)
    except Exception as e:
        logger.error(f"Failed to create volume: {str(e)}")
        raise RuntimeError(f"Failed to create volume: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Remove Volume",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def remove_volume(
    name: str = Field(description="Volume name"),
    force: bool = Field(description="Force removal", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Removing volume {name} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.remove_volume(name, force)
    except Exception as e:
        logger.error(f"Failed to remove volume: {str(e)}")
        raise RuntimeError(f"Failed to remove volume: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Prune Volumes",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def prune_volumes(
    all: bool = Field(description="Remove all volumes (dangerous)", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Pruning volumes for {manager_type}, all: {all}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.prune_volumes(all=all)
    except Exception as e:
        logger.error(f"Failed to prune volumes: {str(e)}")
        raise RuntimeError(f"Failed to prune volumes: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Networks",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def list_networks(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> List[Dict]:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing networks for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_networks()
    except Exception as e:
        logger.error(f"Failed to list networks: {str(e)}")
        raise RuntimeError(f"Failed to list networks: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Create Network",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def create_network(
    name: str = Field(description="Network name"),
    driver: str = Field(description="Network driver (e.g., bridge)", default="bridge"),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Creating network {name} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.create_network(name, driver)
    except Exception as e:
        logger.error(f"Failed to create network: {str(e)}")
        raise RuntimeError(f"Failed to create network: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Remove Network",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def remove_network(
    network_id: str = Field(description="Network ID or name"),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Removing network {network_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.remove_network(network_id)
    except Exception as e:
        logger.error(f"Failed to remove network: {str(e)}")
        raise RuntimeError(f"Failed to remove network: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Prune Networks",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def prune_networks(
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Pruning networks for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.prune_networks()
    except Exception as e:
        logger.error(f"Failed to prune networks: {str(e)}")
        raise RuntimeError(f"Failed to prune networks: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Prune System",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management"},
)
async def prune_system(
    force: bool = Field(description="Force prune", default=False),
    all: bool = Field(description="Prune all unused resources", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Pruning system for {manager_type}, force: {force}, all: {all}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.prune_system(force, all)
    except Exception as e:
        logger.error(f"Failed to prune system: {str(e)}")
        raise RuntimeError(f"Failed to prune system: {str(e)}")


# Swarm-specific tools


@mcp.tool(
    annotations={
        "title": "Init Swarm",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def init_swarm(
    advertise_addr: Optional[str] = Field(
        description="Advertise address", default=None
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Initializing swarm for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.init_swarm(advertise_addr)
    except Exception as e:
        logger.error(f"Failed to init swarm: {str(e)}")
        raise RuntimeError(f"Failed to init swarm: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Leave Swarm",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def leave_swarm(
    force: bool = Field(description="Force leave", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Leaving swarm for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.leave_swarm(force)
    except Exception as e:
        logger.error(f"Failed to leave swarm: {str(e)}")
        raise RuntimeError(f"Failed to leave swarm: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Nodes",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def list_nodes(
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> List[Dict]:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing nodes for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_nodes()
    except Exception as e:
        logger.error(f"Failed to list nodes: {str(e)}")
        raise RuntimeError(f"Failed to list nodes: {str(e)}")


@mcp.tool(
    annotations={
        "title": "List Services",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def list_services(
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> List[Dict]:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Listing services for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.list_services()
    except Exception as e:
        logger.error(f"Failed to list services: {str(e)}")
        raise RuntimeError(f"Failed to list services: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Create Service",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def create_service(
    name: str = Field(description="Service name"),
    image: str = Field(description="Image for the service"),
    replicas: int = Field(description="Number of replicas", default=1),
    ports: Optional[Dict[str, str]] = Field(
        description="Port mappings {target: published}", default=None
    ),
    mounts: Optional[List[str]] = Field(
        description="Mounts [source:target:mode]", default=None
    ),
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Creating service {name} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.create_service(name, image, replicas, ports, mounts)
    except Exception as e:
        logger.error(f"Failed to create service: {str(e)}")
        raise RuntimeError(f"Failed to create service: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Remove Service",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "swarm"},
)
async def remove_service(
    service_id: str = Field(description="Service ID or name"),
    manager_type: Optional[str] = Field(
        description="Container manager: must be docker for swarm (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> Dict:
    if manager_type and manager_type != "docker":
        raise ValueError("Swarm operations are only supported on Docker")
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Removing service {service_id} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.remove_service(service_id)
    except Exception as e:
        logger.error(f"Failed to remove service: {str(e)}")
        raise RuntimeError(f"Failed to remove service: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Compose Up",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
    tags={"container_management", "compose"},
)
async def compose_up(
    compose_file: str = Field(description="Path to compose file"),
    detach: bool = Field(description="Detach mode", default=True),
    build: bool = Field(description="Build images", default=False),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> str:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Compose up {compose_file} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.compose_up(compose_file, detach, build)
    except Exception as e:
        logger.error(f"Failed to compose up: {str(e)}")
        raise RuntimeError(f"Failed to compose up: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Compose Down",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "compose"},
)
async def compose_down(
    compose_file: str = Field(description="Path to compose file"),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> str:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Compose down {compose_file} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.compose_down(compose_file)
    except Exception as e:
        logger.error(f"Failed to compose down: {str(e)}")
        raise RuntimeError(f"Failed to compose down: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Compose Ps",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "compose"},
)
async def compose_ps(
    compose_file: str = Field(description="Path to compose file"),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> str:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Compose ps {compose_file} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.compose_ps(compose_file)
    except Exception as e:
        logger.error(f"Failed to compose ps: {str(e)}")
        raise RuntimeError(f"Failed to compose ps: {str(e)}")


@mcp.tool(
    annotations={
        "title": "Compose Logs",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    tags={"container_management", "compose"},
)
async def compose_logs(
    compose_file: str = Field(description="Path to compose file"),
    service: Optional[str] = Field(description="Specific service", default=None),
    manager_type: Optional[str] = Field(
        description="Container manager: docker, podman (default: auto-detect)",
        default=environment_container_manager_type,
    ),
    silent: Optional[bool] = Field(
        description="Suppress output", default=environment_silent
    ),
    log_file: Optional[str] = Field(
        description="Path to log file", default=environment_log_file
    ),
    ctx: Context = Field(
        description="MCP context for progress reporting", default=None
    ),
) -> str:
    logger = logging.getLogger("ContainerManager")
    logger.debug(
        f"Compose logs {compose_file} for {manager_type}, silent: {silent}, log_file: {log_file}"
    )
    try:
        manager = create_manager(manager_type, silent, log_file)
        return manager.compose_logs(compose_file, service)
    except Exception as e:
        logger.error(f"Failed to compose logs: {str(e)}")
        raise RuntimeError(f"Failed to compose logs: {str(e)}")


def container_manager_mcp():
    parser = argparse.ArgumentParser(description="Container Manager MCP Server")
    parser.add_argument(
        "-t", "--transport", type=str, default="stdio", help="Transport (stdio/http)"
    )
    parser.add_argument("-s", "--host", type=str, default="0.0.0.0", help="Host")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port")
    args = parser.parse_args()

    transport = args.transport
    host = args.host
    port = args.port
    if not (0 <= port <= 65535):
        print(f"Error: Port {port} is out of valid range (0-65535).")
        sys.exit(1)

    setup_logging(is_mcp_server=True, log_file="container_manager_mcp.log")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "http":
        mcp.run(transport="http", host=host, port=port)
    else:
        logger = logging.getLogger("ContainerManager")
        logger.error("Transport not supported")
        sys.exit(1)


def main():
    container_manager_mcp()


if __name__ == "__main__":
    container_manager_mcp()
