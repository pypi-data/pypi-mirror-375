#!/usr/bin/env python
# coding: utf-8

from container_manager.container_manager import (
    main,
    create_manager,
    ContainerManagerBase,
    DockerManager,
    PodmanManager,
)
from container_manager.container_manager_mcp import container_manager_mcp

"""
container-manager

Manage your containers using docker, podman, compose, or docker swarm!
"""

__all__ = [
    "main",
    "create_manager",
    "container_manager_mcp",
    "ContainerManagerBase",
    "DockerManager",
    "PodmanManager",
]
