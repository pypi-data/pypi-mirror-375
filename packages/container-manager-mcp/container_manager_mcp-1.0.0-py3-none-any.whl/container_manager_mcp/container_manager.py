#!/usr/bin/env python
# coding: utf-8

import sys
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import argparse
import json
import subprocess
from datetime import datetime
import dateutil.parser
import platform

try:
    import docker
    from docker.errors import DockerException
except ImportError:
    docker = None
    DockerException = Exception

try:
    from podman import PodmanClient
    from podman.errors import PodmanError
except ImportError:
    PodmanClient = None
    PodmanError = Exception


class ContainerManagerBase(ABC):

    def __init__(self, silent: bool = False, log_file: str = None):
        self.silent = silent
        self.setup_logging(log_file)

    def setup_logging(self, log_file: str):
        if not log_file:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_file = os.path.join(script_dir, "container_manager.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized to {log_file}")

    def log_action(
        self,
        action: str,
        params: Dict = None,
        result: Any = None,
        error: Exception = None,
    ):
        self.logger.info(f"Performing action: {action} with params: {params}")
        if result:
            self.logger.info(f"Result: {result}")
        if error:
            self.logger.error(f"Error: {str(error)}")

    def _format_size(self, size_bytes: int) -> str:
        """Helper to format bytes to human-readable (e.g., 1.23GB)."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return (
                    f"{size_bytes:.2f}{unit}" if unit != "B" else f"{size_bytes}{unit}"
                )
            size_bytes /= 1024.0
        return f"{size_bytes:.2f}PB"

    def _parse_timestamp(self, timestamp: Any) -> str:
        """Parse timestamp (integer or string) to ISO 8601 string."""
        if not timestamp:
            return "unknown"
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")
        if isinstance(timestamp, str):
            try:
                parsed = dateutil.parser.isoparse(timestamp)
                return parsed.strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return "unknown"
        return "unknown"

    @abstractmethod
    def get_version(self) -> Dict:
        pass

    @abstractmethod
    def get_info(self) -> Dict:
        pass

    @abstractmethod
    def list_images(self) -> List[Dict]:
        pass

    @abstractmethod
    def pull_image(
        self, image: str, tag: str = "latest", platform: Optional[str] = None
    ) -> Dict:
        pass

    @abstractmethod
    def remove_image(self, image: str, force: bool = False) -> Dict:
        pass

    @abstractmethod
    def list_containers(self, all: bool = False) -> List[Dict]:
        pass

    @abstractmethod
    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        detach: bool = False,
        ports: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict:
        pass

    @abstractmethod
    def stop_container(self, container_id: str, timeout: int = 10) -> Dict:
        pass

    @abstractmethod
    def remove_container(self, container_id: str, force: bool = False) -> Dict:
        pass

    @abstractmethod
    def get_container_logs(self, container_id: str, tail: str = "all") -> str:
        pass

    @abstractmethod
    def exec_in_container(
        self, container_id: str, command: List[str], detach: bool = False
    ) -> Dict:
        pass

    @abstractmethod
    def list_volumes(self) -> Dict:
        pass

    @abstractmethod
    def create_volume(self, name: str) -> Dict:
        pass

    @abstractmethod
    def remove_volume(self, name: str, force: bool = False) -> Dict:
        pass

    @abstractmethod
    def list_networks(self) -> List[Dict]:
        pass

    @abstractmethod
    def create_network(self, name: str, driver: str = "bridge") -> Dict:
        pass

    @abstractmethod
    def remove_network(self, network_id: str) -> Dict:
        pass

    @abstractmethod
    def compose_up(
        self, compose_file: str, detach: bool = True, build: bool = False
    ) -> str:
        pass

    @abstractmethod
    def compose_down(self, compose_file: str) -> str:
        pass

    @abstractmethod
    def compose_ps(self, compose_file: str) -> str:
        pass

    @abstractmethod
    def compose_logs(self, compose_file: str, service: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def init_swarm(self, advertise_addr: Optional[str] = None) -> Dict:
        pass

    @abstractmethod
    def leave_swarm(self, force: bool = False) -> Dict:
        pass

    @abstractmethod
    def list_nodes(self) -> List[Dict]:
        pass

    @abstractmethod
    def list_services(self) -> List[Dict]:
        pass

    @abstractmethod
    def create_service(
        self,
        name: str,
        image: str,
        replicas: int = 1,
        ports: Optional[Dict[str, str]] = None,
        mounts: Optional[List[str]] = None,
    ) -> Dict:
        pass

    @abstractmethod
    def remove_service(self, service_id: str) -> Dict:
        pass


class DockerManager(ContainerManagerBase):
    def __init__(self, silent: bool = False, log_file: str = None):
        super().__init__(silent, log_file)
        if docker is None:
            raise ImportError("Please install docker-py: pip install docker")
        try:
            self.client = docker.from_env()
        except DockerException as e:
            self.logger.error(f"Failed to connect to Docker daemon: {str(e)}")
            raise RuntimeError(f"Failed to connect to Docker: {str(e)}")

    def list_images(self) -> List[Dict]:
        params = {}
        try:
            images = self.client.images.list()
            result = []
            for img in images:
                attrs = img.attrs
                repo_tags = attrs.get("RepoTags", [])
                repo_tag = repo_tags[0] if repo_tags else "<none>:<none>"
                repository, tag = (
                    repo_tag.rsplit(":", 1) if ":" in repo_tag else ("<none>", "<none>")
                )

                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)

                size_bytes = attrs.get("Size", 0)
                size_str = self._format_size(size_bytes) if size_bytes else "0B"

                simplified = {
                    "repository": repository,
                    "tag": tag,
                    "id": (
                        attrs.get("Id", "unknown")[7:19]
                        if attrs.get("Id")
                        else "unknown"
                    ),
                    "created": created_str,
                    "size": size_str,
                }
                result.append(simplified)

            self.log_action("list_images", params, result)
            return result
        except Exception as e:
            self.log_action("list_images", params, error=e)
            raise RuntimeError(f"Failed to list images: {str(e)}")

    def pull_image(
        self, image: str, tag: str = "latest", platform: Optional[str] = None
    ) -> Dict:
        params = {"image": image, "tag": tag, "platform": platform}
        try:
            img = self.client.images.pull(f"{image}:{tag}", platform=platform)
            attrs = img.attrs
            repo_tags = attrs.get("RepoTags", [])
            repo_tag = repo_tags[0] if repo_tags else f"{image}:{tag}"
            repository, tag = (
                repo_tag.rsplit(":", 1) if ":" in repo_tag else (image, tag)
            )
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            size_bytes = attrs.get("Size", 0)
            size_str = self._format_size(size_bytes) if size_bytes else "0B"
            result = {
                "repository": repository,
                "tag": tag,
                "id": (
                    attrs.get("Id", "unknown")[7:19] if attrs.get("Id") else "unknown"
                ),
                "created": created_str,
                "size": size_str,
            }
            self.log_action("pull_image", params, result)
            return result
        except Exception as e:
            self.log_action("pull_image", params, error=e)
            raise RuntimeError(f"Failed to pull image: {str(e)}")

    def list_containers(self, all: bool = False) -> List[Dict]:
        params = {"all": all}
        try:
            containers = self.client.containers.list(all=all)
            result = []
            for c in containers:
                attrs = c.attrs
                ports = attrs.get("NetworkSettings", {}).get("Ports", {})
                port_mappings = []
                for container_port, host_ports in ports.items():
                    if host_ports:
                        for hp in host_ports:
                            port_mappings.append(
                                f"{hp.get('HostIp', '0.0.0.0')}:{hp.get('HostPort')}->{container_port}"
                            )
                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)
                simplified = {
                    "id": attrs.get("Id", "unknown")[7:19],
                    "image": attrs.get("Config", {}).get("Image", "unknown"),
                    "name": attrs.get("Name", "unknown").lstrip("/"),
                    "status": attrs.get("State", {}).get("Status", "unknown"),
                    "ports": ", ".join(port_mappings) if port_mappings else "none",
                    "created": created_str,
                }
                result.append(simplified)
            self.log_action("list_containers", params, result)
            return result
        except Exception as e:
            self.log_action("list_containers", params, error=e)
            raise RuntimeError(f"Failed to list containers: {str(e)}")

    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        detach: bool = False,
        ports: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict:
        params = {
            "image": image,
            "name": name,
            "command": command,
            "detach": detach,
            "ports": ports,
            "volumes": volumes,
            "environment": environment,
        }
        try:
            container = self.client.containers.run(
                image,
                command=command,
                name=name,
                detach=detach,
                ports=ports,
                volumes=volumes,
                environment=environment,
            )
            if not detach:
                result = {"output": container.decode("utf-8") if container else ""}
                self.log_action("run_container", params, result)
                return result
            attrs = container.attrs
            ports = attrs.get("NetworkSettings", {}).get("Ports", {})
            port_mappings = []
            for container_port, host_ports in ports.items():
                if host_ports:
                    for hp in host_ports:
                        port_mappings.append(
                            f"{hp.get('HostIp', '0.0.0.0')}:{hp.get('HostPort')}->{container_port}"
                        )
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            result = {
                "id": attrs.get("Id", "unknown")[7:19],
                "image": attrs.get("Config", {}).get("Image", image),
                "name": attrs.get("Name", name or "unknown").lstrip("/"),
                "status": attrs.get("State", {}).get("Status", "unknown"),
                "ports": ", ".join(port_mappings) if port_mappings else "none",
                "created": created_str,
            }
            self.log_action("run_container", params, result)
            return result
        except Exception as e:
            self.log_action("run_container", params, error=e)
            raise RuntimeError(f"Failed to run container: {str(e)}")

    def list_networks(self) -> List[Dict]:
        params = {}
        try:
            networks = self.client.networks.list()
            result = []
            for net in networks:
                attrs = net.attrs
                containers = len(attrs.get("Containers", {}))
                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)
                simplified = {
                    "id": attrs.get("Id", "unknown")[7:19],
                    "name": attrs.get("Name", "unknown"),
                    "driver": attrs.get("Driver", "unknown"),
                    "scope": attrs.get("Scope", "unknown"),
                    "containers": containers,
                    "created": created_str,
                }
                result.append(simplified)
            self.log_action("list_networks", params, result)
            return result
        except Exception as e:
            self.log_action("list_networks", params, error=e)
            raise RuntimeError(f"Failed to list networks: {str(e)}")

    def create_network(self, name: str, driver: str = "bridge") -> Dict:
        params = {"name": name, "driver": driver}
        try:
            network = self.client.networks.create(name, driver=driver)
            attrs = network.attrs
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            result = {
                "id": attrs.get("Id", "unknown")[7:19],
                "name": attrs.get("Name", name),
                "driver": attrs.get("Driver", driver),
                "scope": attrs.get("Scope", "unknown"),
                "created": created_str,
            }
            self.log_action("create_network", params, result)
            return result
        except Exception as e:
            self.log_action("create_network", params, error=e)
            raise RuntimeError(f"Failed to create network: {str(e)}")

    def get_version(self) -> Dict:
        params = {}
        try:
            version = self.client.version()
            result = {
                "version": version.get("Version", "unknown"),
                "api_version": version.get("ApiVersion", "unknown"),
                "os": version.get("Os", "unknown"),
                "arch": version.get("Arch", "unknown"),
                "build_time": version.get("BuildTime", "unknown"),
            }
            self.log_action("get_version", params, result)
            return result
        except Exception as e:
            self.log_action("get_version", params, error=e)
            raise RuntimeError(f"Failed to get version: {str(e)}")

    def get_info(self) -> Dict:
        params = {}
        try:
            info = self.client.info()
            result = {
                "containers_total": info.get("Containers", 0),
                "containers_running": info.get("ContainersRunning", 0),
                "images": info.get("Images", 0),
                "driver": info.get("Driver", "unknown"),
                "platform": f"{info.get('OperatingSystem', 'unknown')} {info.get('Architecture', 'unknown')}",
                "memory_total": self._format_size(info.get("MemTotal", 0)),
                "swap_total": self._format_size(info.get("SwapTotal", 0)),
            }
            self.log_action("get_info", params, result)
            return result
        except Exception as e:
            self.log_action("get_info", params, error=e)
            raise RuntimeError(f"Failed to get info: {str(e)}")

    def remove_image(self, image: str, force: bool = False) -> Dict:
        params = {"image": image, "force": force}
        try:
            self.client.images.remove(image, force=force)
            result = {"removed": image}
            self.log_action("remove_image", params, result)
            return result
        except Exception as e:
            self.log_action("remove_image", params, error=e)
            raise RuntimeError(f"Failed to remove image: {str(e)}")

    def stop_container(self, container_id: str, timeout: int = 10) -> Dict:
        params = {"container_id": container_id, "timeout": timeout}
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            result = {"stopped": container_id}
            self.log_action("stop_container", params, result)
            return result
        except Exception as e:
            self.log_action("stop_container", params, error=e)
            raise RuntimeError(f"Failed to stop container: {str(e)}")

    def remove_container(self, container_id: str, force: bool = False) -> Dict:
        params = {"container_id": container_id, "force": force}
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            result = {"removed": container_id}
            self.log_action("remove_container", params, result)
            return result
        except Exception as e:
            self.log_action("remove_container", params, error=e)
            raise RuntimeError(f"Failed to remove container: {str(e)}")

    def get_container_logs(self, container_id: str, tail: str = "all") -> str:
        params = {"container_id": container_id, "tail": tail}
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode("utf-8")
            self.log_action(
                "get_container_logs", params, logs[:1000]
            )  # Truncate for logging
            return logs
        except Exception as e:
            self.log_action("get_container_logs", params, error=e)
            raise RuntimeError(f"Failed to get container logs: {str(e)}")

    def exec_in_container(
        self, container_id: str, command: List[str], detach: bool = False
    ) -> Dict:
        params = {"container_id": container_id, "command": command, "detach": detach}
        try:
            container = self.client.containers.get(container_id)
            exit_code, output = container.exec_run(command, detach=detach)
            result = {
                "exit_code": exit_code,
                "output": output.decode("utf-8") if output and not detach else None,
                "command": command,
            }
            self.log_action("exec_in_container", params, result)
            return result
        except Exception as e:
            self.log_action("exec_in_container", params, error=e)
            raise RuntimeError(f"Failed to exec in container: {str(e)}")

    def list_volumes(self) -> Dict:
        params = {}
        try:
            volumes = self.client.volumes.list()
            result = {
                "volumes": [
                    {
                        "name": v.attrs.get("Name", "unknown"),
                        "driver": v.attrs.get("Driver", "unknown"),
                        "mountpoint": v.attrs.get("Mountpoint", "unknown"),
                        "created": v.attrs.get("CreatedAt", "unknown"),
                    }
                    for v in volumes
                ]
            }
            self.log_action("list_volumes", params, result)
            return result
        except Exception as e:
            self.log_action("list_volumes", params, error=e)
            raise RuntimeError(f"Failed to list volumes: {str(e)}")

    def create_volume(self, name: str) -> Dict:
        params = {"name": name}
        try:
            volume = self.client.volumes.create(name=name)
            attrs = volume.attrs
            result = {
                "name": attrs.get("Name", name),
                "driver": attrs.get("Driver", "unknown"),
                "mountpoint": attrs.get("Mountpoint", "unknown"),
                "created": attrs.get("CreatedAt", "unknown"),
            }
            self.log_action("create_volume", params, result)
            return result
        except Exception as e:
            self.log_action("create_volume", params, error=e)
            raise RuntimeError(f"Failed to create volume: {str(e)}")

    def remove_volume(self, name: str, force: bool = False) -> Dict:
        params = {"name": name, "force": force}
        try:
            volume = self.client.volumes.get(name)
            volume.remove(force=force)
            result = {"removed": name}
            self.log_action("remove_volume", params, result)
            return result
        except Exception as e:
            self.log_action("remove_volume", params, error=e)
            raise RuntimeError(f"Failed to remove volume: {str(e)}")

    def remove_network(self, network_id: str) -> Dict:
        params = {"network_id": network_id}
        try:
            network = self.client.networks.get(network_id)
            network.remove()
            result = {"removed": network_id}
            self.log_action("remove_network", params, result)
            return result
        except Exception as e:
            self.log_action("remove_network", params, error=e)
            raise RuntimeError(f"Failed to remove network: {str(e)}")

    def compose_up(
        self, compose_file: str, detach: bool = True, build: bool = False
    ) -> str:
        params = {"compose_file": compose_file, "detach": detach, "build": build}
        try:
            cmd = ["docker", "compose", "-f", compose_file, "up"]
            if build:
                cmd.append("--build")
            if detach:
                cmd.append("-d")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_up", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_up", params, error=e)
            raise RuntimeError(f"Failed to compose up: {str(e)}")

    def compose_down(self, compose_file: str) -> str:
        params = {"compose_file": compose_file}
        try:
            cmd = ["docker", "compose", "-f", compose_file, "down"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_down", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_down", params, error=e)
            raise RuntimeError(f"Failed to compose down: {str(e)}")

    def compose_ps(self, compose_file: str) -> str:
        params = {"compose_file": compose_file}
        try:
            cmd = ["docker", "compose", "-f", compose_file, "ps"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_ps", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_ps", params, error=e)
            raise RuntimeError(f"Failed to compose ps: {str(e)}")

    def compose_logs(self, compose_file: str, service: Optional[str] = None) -> str:
        params = {"compose_file": compose_file, "service": service}
        try:
            cmd = ["docker", "compose", "-f", compose_file, "logs"]
            if service:
                cmd.append(service)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_logs", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_logs", params, error=e)
            raise RuntimeError(f"Failed to compose logs: {str(e)}")

    def init_swarm(self, advertise_addr: Optional[str] = None) -> Dict:
        params = {"advertise_addr": advertise_addr}
        try:
            swarm_id = self.client.swarm.init(advertise_addr=advertise_addr)
            result = {"swarm_id": swarm_id}
            self.log_action("init_swarm", params, result)
            return result
        except Exception as e:
            self.log_action("init_swarm", params, error=e)
            raise RuntimeError(f"Failed to init swarm: {str(e)}")

    def leave_swarm(self, force: bool = False) -> Dict:
        params = {"force": force}
        try:
            self.client.swarm.leave(force=force)
            result = {"left": True}
            self.log_action("leave_swarm", params, result)
            return result
        except Exception as e:
            self.log_action("leave_swarm", params, error=e)
            raise RuntimeError(f"Failed to leave swarm: {str(e)}")

    def list_nodes(self) -> List[Dict]:
        params = {}
        try:
            nodes = self.client.nodes.list()
            result = []
            for node in nodes:
                attrs = node.attrs
                spec = attrs.get("Spec", {})
                status = attrs.get("Status", {})
                created = attrs.get("CreatedAt", "unknown")
                updated = attrs.get("UpdatedAt", "unknown")
                simplified = {
                    "id": attrs.get("ID", "unknown")[7:19],
                    "hostname": spec.get("Name", "unknown"),
                    "role": spec.get("Role", "unknown"),
                    "status": status.get("State", "unknown"),
                    "availability": spec.get("Availability", "unknown"),
                    "created": created,
                    "updated": updated,
                }
                result.append(simplified)
            self.log_action("list_nodes", params, result)
            return result
        except Exception as e:
            self.log_action("list_nodes", params, error=e)
            raise RuntimeError(f"Failed to list nodes: {str(e)}")

    def list_services(self) -> List[Dict]:
        params = {}
        try:
            services = self.client.services.list()
            result = []
            for service in services:
                attrs = service.attrs
                spec = attrs.get("Spec", {})
                endpoint = attrs.get("Endpoint", {})
                ports = endpoint.get("Ports", [])
                port_mappings = [
                    f"{p.get('PublishedPort')}->{p.get('TargetPort')}/{p.get('Protocol')}"
                    for p in ports
                    if p.get("PublishedPort")
                ]
                created = attrs.get("CreatedAt", "unknown")
                updated = attrs.get("UpdatedAt", "unknown")
                simplified = {
                    "id": attrs.get("ID", "unknown")[7:19],
                    "name": spec.get("Name", "unknown"),
                    "image": spec.get("TaskTemplate", {})
                    .get("ContainerSpec", {})
                    .get("Image", "unknown"),
                    "replicas": spec.get("Mode", {})
                    .get("Replicated", {})
                    .get("Replicas", 0),
                    "ports": ", ".join(port_mappings) if port_mappings else "none",
                    "created": created,
                    "updated": updated,
                }
                result.append(simplified)
            self.log_action("list_services", params, result)
            return result
        except Exception as e:
            self.log_action("list_services", params, error=e)
            raise RuntimeError(f"Failed to list services: {str(e)}")

    def create_service(
        self,
        name: str,
        image: str,
        replicas: int = 1,
        ports: Optional[Dict[str, str]] = None,
        mounts: Optional[List[str]] = None,
    ) -> Dict:
        params = {
            "name": name,
            "image": image,
            "replicas": replicas,
            "ports": ports,
            "mounts": mounts,
        }
        try:
            mode = {"mode": "replicated", "replicas": replicas}
            endpoint_spec = None
            if ports:
                port_list = [
                    {
                        "Protocol": "tcp",
                        "PublishedPort": int(host_port),
                        "TargetPort": int(container_port.split("/")[0]),
                    }
                    for container_port, host_port in ports.items()
                ]
                endpoint_spec = docker.types.EndpointSpec(ports=port_list)
            service = self.client.services.create(
                image,
                name=name,
                mode=mode,
                mounts=mounts,
                endpoint_spec=endpoint_spec,
            )
            attrs = service.attrs
            spec = attrs.get("Spec", {})
            endpoint = attrs.get("Endpoint", {})
            ports = endpoint.get("Ports", [])
            port_mappings = [
                f"{p.get('PublishedPort')}->{p.get('TargetPort')}/{p.get('Protocol')}"
                for p in ports
                if p.get("PublishedPort")
            ]
            created = attrs.get("CreatedAt", "unknown")
            result = {
                "id": attrs.get("ID", "unknown")[7:19],
                "name": spec.get("Name", name),
                "image": spec.get("TaskTemplate", {})
                .get("ContainerSpec", {})
                .get("Image", image),
                "replicas": spec.get("Mode", {})
                .get("Replicated", {})
                .get("Replicas", replicas),
                "ports": ", ".join(port_mappings) if port_mappings else "none",
                "created": created,
            }
            self.log_action("create_service", params, result)
            return result
        except Exception as e:
            self.log_action("create_service", params, error=e)
            raise RuntimeError(f"Failed to create service: {str(e)}")

    def remove_service(self, service_id: str) -> Dict:
        params = {"service_id": service_id}
        try:
            service = self.client.services.get(service_id)
            service.remove()
            result = {"removed": service_id}
            self.log_action("remove_service", params, result)
            return result
        except Exception as e:
            self.log_action("remove_service", params, error=e)
            raise RuntimeError(f"Failed to remove service: {str(e)}")


class PodmanManager(ContainerManagerBase):
    def __init__(self, silent: bool = False, log_file: Optional[str] = None):
        super().__init__(silent, log_file)

        if PodmanClient is None:
            raise ImportError("Please install podman-py: pip install podman")

        base_url = self._autodetect_podman_url()
        if base_url is None:
            self.logger.error(
                "No valid Podman socket found after trying all known locations"
            )
            raise RuntimeError("Failed to connect to Podman: No valid socket found")

        try:
            self.client = PodmanClient(base_url=base_url)
            self.logger.info(f"Connected to Podman with base_url: {base_url}")
        except PodmanError as e:
            self.logger.error(
                f"Failed to connect to Podman daemon with {base_url}: {str(e)}"
            )
            raise RuntimeError(f"Failed to connect to Podman with {base_url}: {str(e)}")

    def _is_wsl(self) -> bool:
        """Check if running inside WSL2."""
        try:
            with open("/proc/version", "r") as f:
                return "WSL" in f.read()
        except FileNotFoundError:
            return "WSL_DISTRO_NAME" in os.environ

    def _is_podman_machine_running(self) -> bool:
        """Check if Podman machine is running (for Windows/WSL2)."""
        try:
            result = subprocess.run(
                ["podman", "machine", "list", "--format", "{{.Running}}"],
                capture_output=True,
                text=True,
                check=False,
            )
            return "true" in result.stdout.lower()
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _try_connect(self, base_url: str) -> Optional[PodmanClient]:
        """Attempt to connect to Podman with the given base_url."""
        try:
            client = PodmanClient(base_url=base_url)
            # Test connection
            client.version()
            return client
        except PodmanError as e:
            self.logger.debug(f"Connection failed for {base_url}: {str(e)}")
            return None

    def _autodetect_podman_url(self) -> Optional[str]:
        """Autodetect the appropriate Podman socket URL based on platform."""
        # Check for environment variable override
        base_url = os.environ.get("PODMAN_BASE_URL")
        if base_url:
            self.logger.info(f"Using PODMAN_BASE_URL from environment: {base_url}")
            return base_url

        system = platform.system()
        is_wsl = self._is_wsl()

        # Define socket candidates based on platform
        socket_candidates = []
        if system == "Windows" and not is_wsl:
            # Windows with Podman machine
            if self._is_podman_machine_running():
                socket_candidates.append("npipe:////./pipe/docker_engine")
            # Fallback to WSL2 distro sockets if running in a mixed setup
            socket_candidates.extend(
                [
                    "unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-user.sock",  # Rootless
                    "unix:///mnt/wsl/podman-sockets/podman-machine-default/podman-root.sock",  # Rootful
                ]
            )
        elif system == "Linux" or is_wsl:
            # Linux or WSL2 distro: prioritize rootless, then rootful
            uid = os.getuid()
            socket_candidates.extend(
                [
                    f"unix:///run/user/{uid}/podman/podman.sock",  # Rootless
                    "unix:///run/podman/podman.sock",  # Rootful
                ]
            )

        # Try each socket candidate
        for url in socket_candidates:
            # For Unix sockets, check if the file exists (on Linux/WSL2)
            if url.startswith("unix://") and (system == "Linux" or is_wsl):
                socket_path = url.replace("unix://", "")
                if not os.path.exists(socket_path):
                    self.logger.debug(f"Socket {socket_path} does not exist")
                    continue
            client = self._try_connect(url)
            if client:
                return url

        return None

    def list_images(self) -> List[Dict]:
        params = {}
        try:
            images = self.client.images.list()
            result = []
            for img in images:
                attrs = img.attrs
                repo_tags = attrs.get("Names", [])
                repo_tag = repo_tags[0] if repo_tags else "<none>:<none>"
                repository, tag = (
                    repo_tag.rsplit(":", 1) if ":" in repo_tag else ("<none>", "<none>")
                )
                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)
                size_bytes = attrs.get("Size", 0)
                size_str = self._format_size(size_bytes) if size_bytes else "0B"
                simplified = {
                    "repository": repository,
                    "tag": tag,
                    "id": (
                        attrs.get("Id", "unknown")[7:19]
                        if attrs.get("Id")
                        else "unknown"
                    ),
                    "created": created_str,
                    "size": size_str,
                }
                result.append(simplified)
            self.log_action("list_images", params, result)
            return result
        except Exception as e:
            self.log_action("list_images", params, error=e)
            raise RuntimeError(f"Failed to list images: {str(e)}")

    def pull_image(
        self, image: str, tag: str = "latest", platform: Optional[str] = None
    ) -> Dict:
        params = {"image": image, "tag": tag, "platform": platform}
        try:
            img = self.client.images.pull(f"{image}:{tag}", platform=platform)
            attrs = img[0].attrs if isinstance(img, list) else img.attrs
            repo_tags = attrs.get("Names", [])
            repo_tag = repo_tags[0] if repo_tags else f"{image}:{tag}"
            repository, tag = (
                repo_tag.rsplit(":", 1) if ":" in repo_tag else (image, tag)
            )
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            size_bytes = attrs.get("Size", 0)
            size_str = self._format_size(size_bytes) if size_bytes else "0B"
            result = {
                "repository": repository,
                "tag": tag,
                "id": (
                    attrs.get("Id", "unknown")[7:19] if attrs.get("Id") else "unknown"
                ),
                "created": created_str,
                "size": size_str,
            }
            self.log_action("pull_image", params, result)
            return result
        except Exception as e:
            self.log_action("pull_image", params, error=e)
            raise RuntimeError(f"Failed to pull image: {str(e)}")

    def list_containers(self, all: bool = False) -> List[Dict]:
        params = {"all": all}
        try:
            containers = self.client.containers.list(all=all)
            result = []
            for c in containers:
                attrs = c.attrs
                ports = attrs.get("Ports", [])
                port_mappings = [
                    f"{p.get('host_ip', '0.0.0.0')}:{p.get('host_port')}->{p.get('container_port')}/{p.get('protocol', 'tcp')}"
                    for p in ports
                    if p.get("host_port")
                ]
                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)
                simplified = {
                    "id": attrs.get("Id", "unknown")[7:19],
                    "image": attrs.get("Image", "unknown"),
                    "name": attrs.get("Names", ["unknown"])[0].lstrip("/"),
                    "status": attrs.get("State", "unknown"),
                    "ports": ", ".join(port_mappings) if port_mappings else "none",
                    "created": created_str,
                }
                result.append(simplified)
            self.log_action("list_containers", params, result)
            return result
        except Exception as e:
            self.log_action("list_containers", params, error=e)
            raise RuntimeError(f"Failed to list containers: {str(e)}")

    def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        detach: bool = False,
        ports: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict]] = None,
        environment: Optional[Dict[str, str]] = None,
    ) -> Dict:
        params = {
            "image": image,
            "name": name,
            "command": command,
            "detach": detach,
            "ports": ports,
            "volumes": volumes,
            "environment": environment,
        }
        try:
            container = self.client.containers.run(
                image,
                command=command,
                name=name,
                detach=detach,
                ports=ports,
                volumes=volumes,
                environment=environment,
            )
            if not detach:
                result = {"output": container.decode("utf-8") if container else ""}
                self.log_action("run_container", params, result)
                return result
            attrs = container.attrs
            ports = attrs.get("Ports", [])
            port_mappings = [
                f"{p.get('host_ip', '0.0.0.0')}:{p.get('host_port')}->{p.get('container_port')}/{p.get('protocol', 'tcp')}"
                for p in ports
                if p.get("host_port")
            ]
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            result = {
                "id": attrs.get("Id", "unknown")[7:19],
                "image": attrs.get("Image", image),
                "name": attrs.get("Names", [name or "unknown"])[0].lstrip("/"),
                "status": attrs.get("State", "unknown"),
                "ports": ", ".join(port_mappings) if port_mappings else "none",
                "created": created_str,
            }
            self.log_action("run_container", params, result)
            return result
        except Exception as e:
            self.log_action("run_container", params, error=e)
            raise RuntimeError(f"Failed to run container: {str(e)}")

    def list_networks(self) -> List[Dict]:
        params = {}
        try:
            networks = self.client.networks.list()
            result = []
            for net in networks:
                attrs = net.attrs
                containers = len(attrs.get("Containers", {}))
                created = attrs.get("Created", None)
                created_str = self._parse_timestamp(created)
                simplified = {
                    "id": attrs.get("Id", "unknown")[7:19],
                    "name": attrs.get("Name", "unknown"),
                    "driver": attrs.get("Driver", "unknown"),
                    "scope": attrs.get("Scope", "unknown"),
                    "containers": containers,
                    "created": created_str,
                }
                result.append(simplified)
            self.log_action("list_networks", params, result)
            return result
        except Exception as e:
            self.log_action("list_networks", params, error=e)
            raise RuntimeError(f"Failed to list networks: {str(e)}")

    def create_network(self, name: str, driver: str = "bridge") -> Dict:
        params = {"name": name, "driver": driver}
        try:
            network = self.client.networks.create(name, driver=driver)
            attrs = network.attrs
            created = attrs.get("Created", None)
            created_str = self._parse_timestamp(created)
            result = {
                "id": attrs.get("Id", "unknown")[7:19],
                "name": attrs.get("Name", name),
                "driver": attrs.get("Driver", driver),
                "scope": attrs.get("Scope", "unknown"),
                "created": created_str,
            }
            self.log_action("create_network", params, result)
            return result
        except Exception as e:
            self.log_action("create_network", params, error=e)
            raise RuntimeError(f"Failed to create network: {str(e)}")

    def get_version(self) -> Dict:
        params = {}
        try:
            version = self.client.version()
            result = {
                "version": version.get("Version", "unknown"),
                "api_version": version.get("APIVersion", "unknown"),
                "os": version.get("Os", "unknown"),
                "arch": version.get("Arch", "unknown"),
                "build_time": version.get("BuildTime", "unknown"),
            }
            self.log_action("get_version", params, result)
            return result
        except Exception as e:
            self.log_action("get_version", params, error=e)
            raise RuntimeError(f"Failed to get version: {str(e)}")

    def get_info(self) -> Dict:
        params = {}
        try:
            info = self.client.info()
            host = info.get("host", {})
            result = {
                "containers_total": info.get("store", {}).get("containers", 0),
                "containers_running": host.get("runningContainers", 0),
                "images": info.get("store", {}).get("images", 0),
                "driver": host.get("graphDriverName", "unknown"),
                "platform": f"{host.get('os', 'unknown')} {host.get('arch', 'unknown')}",
                "memory_total": self._format_size(host.get("memTotal", 0)),
                "swap_total": self._format_size(host.get("swapTotal", 0)),
            }
            self.log_action("get_info", params, result)
            return result
        except Exception as e:
            self.log_action("get_info", params, error=e)
            raise RuntimeError(f"Failed to get info: {str(e)}")

    def remove_image(self, image: str, force: bool = False) -> Dict:
        params = {"image": image, "force": force}
        try:
            self.client.images.remove(image, force=force)
            result = {"removed": image}
            self.log_action("remove_image", params, result)
            return result
        except Exception as e:
            self.log_action("remove_image", params, error=e)
            raise RuntimeError(f"Failed to remove image: {str(e)}")

    def stop_container(self, container_id: str, timeout: int = 10) -> Dict:
        params = {"container_id": container_id, "timeout": timeout}
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            result = {"stopped": container_id}
            self.log_action("stop_container", params, result)
            return result
        except Exception as e:
            self.log_action("stop_container", params, error=e)
            raise RuntimeError(f"Failed to stop container: {str(e)}")

    def remove_container(self, container_id: str, force: bool = False) -> Dict:
        params = {"container_id": container_id, "force": force}
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            result = {"removed": container_id}
            self.log_action("remove_container", params, result)
            return result
        except Exception as e:
            self.log_action("remove_container", params, error=e)
            raise RuntimeError(f"Failed to remove container: {str(e)}")

    def get_container_logs(self, container_id: str, tail: str = "all") -> str:
        params = {"container_id": container_id, "tail": tail}
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode("utf-8")
            self.log_action(
                "get_container_logs", params, logs[:1000]
            )  # Truncate for logging
            return logs
        except Exception as e:
            self.log_action("get_container_logs", params, error=e)
            raise RuntimeError(f"Failed to get container logs: {str(e)}")

    def exec_in_container(
        self, container_id: str, command: List[str], detach: bool = False
    ) -> Dict:
        params = {"container_id": container_id, "command": command, "detach": detach}
        try:
            container = self.client.containers.get(container_id)
            exit_code, output = container.exec_run(command, detach=detach)
            result = {
                "exit_code": exit_code,
                "output": output.decode("utf-8") if output and not detach else None,
                "command": command,
            }
            self.log_action("exec_in_container", params, result)
            return result
        except Exception as e:
            self.log_action("exec_in_container", params, error=e)
            raise RuntimeError(f"Failed to exec in container: {str(e)}")

    def list_volumes(self) -> Dict:
        params = {}
        try:
            volumes = self.client.volumes.list()
            result = {
                "volumes": [
                    {
                        "name": v.attrs.get("Name", "unknown"),
                        "driver": v.attrs.get("Driver", "unknown"),
                        "mountpoint": v.attrs.get("Mountpoint", "unknown"),
                        "created": v.attrs.get("CreatedAt", "unknown"),
                    }
                    for v in volumes
                ]
            }
            self.log_action("list_volumes", params, result)
            return result
        except Exception as e:
            self.log_action("list_volumes", params, error=e)
            raise RuntimeError(f"Failed to list volumes: {str(e)}")

    def create_volume(self, name: str) -> Dict:
        params = {"name": name}
        try:
            volume = self.client.volumes.create(name=name)
            attrs = volume.attrs
            result = {
                "name": attrs.get("Name", name),
                "driver": attrs.get("Driver", "unknown"),
                "mountpoint": attrs.get("Mountpoint", "unknown"),
                "created": attrs.get("CreatedAt", "unknown"),
            }
            self.log_action("create_volume", params, result)
            return result
        except Exception as e:
            self.log_action("create_volume", params, error=e)
            raise RuntimeError(f"Failed to create volume: {str(e)}")

    def remove_volume(self, name: str, force: bool = False) -> Dict:
        params = {"name": name, "force": force}
        try:
            volume = self.client.volumes.get(name)
            volume.remove(force=force)
            result = {"removed": name}
            self.log_action("remove_volume", params, result)
            return result
        except Exception as e:
            self.log_action("remove_volume", params, error=e)
            raise RuntimeError(f"Failed to remove volume: {str(e)}")

    def remove_network(self, network_id: str) -> Dict:
        params = {"network_id": network_id}
        try:
            network = self.client.networks.get(network_id)
            network.remove()
            result = {"removed": network_id}
            self.log_action("remove_network", params, result)
            return result
        except Exception as e:
            self.log_action("remove_network", params, error=e)
            raise RuntimeError(f"Failed to remove network: {str(e)}")

    def compose_up(
        self, compose_file: str, detach: bool = True, build: bool = False
    ) -> str:
        params = {"compose_file": compose_file, "detach": detach, "build": build}
        try:
            cmd = ["podman-compose", "-f", compose_file, "up"]
            if build:
                cmd.append("--build")
            if detach:
                cmd.append("-d")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_up", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_up", params, error=e)
            raise RuntimeError(f"Failed to compose up: {str(e)}")

    def compose_down(self, compose_file: str) -> str:
        params = {"compose_file": compose_file}
        try:
            cmd = ["podman-compose", "-f", compose_file, "down"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_down", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_down", params, error=e)
            raise RuntimeError(f"Failed to compose down: {str(e)}")

    def compose_ps(self, compose_file: str) -> str:
        params = {"compose_file": compose_file}
        try:
            cmd = ["podman-compose", "-f", compose_file, "ps"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_ps", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_ps", params, error=e)
            raise RuntimeError(f"Failed to compose ps: {str(e)}")

    def compose_logs(self, compose_file: str, service: Optional[str] = None) -> str:
        params = {"compose_file": compose_file, "service": service}
        try:
            cmd = ["podman-compose", "-f", compose_file, "logs"]
            if service:
                cmd.append(service)
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            self.log_action("compose_logs", params, result.stdout)
            return result.stdout
        except Exception as e:
            self.log_action("compose_logs", params, error=e)
            raise RuntimeError(f"Failed to compose logs: {str(e)}")

    def init_swarm(self, advertise_addr: Optional[str] = None) -> Dict:
        raise NotImplementedError("Swarm not supported in Podman")

    def leave_swarm(self, force: bool = False) -> Dict:
        raise NotImplementedError("Swarm not supported in Podman")

    def list_nodes(self) -> List[Dict]:
        raise NotImplementedError("Swarm not supported in Podman")

    def list_services(self) -> List[Dict]:
        raise NotImplementedError("Swarm not supported in Podman")

    def create_service(
        self,
        name: str,
        image: str,
        replicas: int = 1,
        ports: Optional[Dict[str, str]] = None,
        mounts: Optional[List[str]] = None,
    ) -> Dict:
        raise NotImplementedError("Swarm not supported in Podman")

    def remove_service(self, service_id: str) -> Dict:
        raise NotImplementedError("Swarm not supported in Podman")


def create_manager(
    manager_type: Optional[str] = None, silent: bool = False, log_file: str = None
) -> ContainerManagerBase:
    if manager_type is None:
        manager_type = os.environ.get("CONTAINER_MANAGER_TYPE")
    if manager_type is None:
        # Autodetect
        if PodmanClient is not None:
            try:
                test_client = PodmanClient()
                test_client.close()
                manager_type = "podman"
            except Exception:
                pass
        if manager_type is None and docker is not None:
            try:
                test_client = docker.from_env()
                test_client.close()
                manager_type = "docker"
            except Exception:
                pass
    if manager_type is None:
        raise ValueError(
            "No supported container manager detected. Set CONTAINER_MANAGER_TYPE or install Docker/Podman."
        )
    if manager_type.lower() in ["docker", "swarm"]:
        return DockerManager(silent=silent, log_file=log_file)
    elif manager_type.lower() == "podman":
        return PodmanManager(silent=silent, log_file=log_file)
    else:
        raise ValueError(f"Unsupported container manager type: {manager_type}")


def usage():
    print(
        """
Container Manager: A tool to manage containers with Docker, Podman, and Docker Swarm!

Usage:
-h | --help            [ See usage for script ]
-s | --silent          [ Suppress output ]
-m | --manager <type>  [ docker, podman, swarm; default: auto-detect ]
--log-file <path>      [ Log to specified file (default: container_manager.log in script dir) ]

Actions:
--get-version          [ Get version info ]
--get-info             [ Get system info ]
--list-images          [ List images ]
--pull-image <image>   [ Pull image, e.g., nginx ]
  --tag <tag>          [ Tag, default: latest ]
  --platform <plat>    [ Platform, e.g., linux/amd64 ]
--remove-image <image> [ Remove image ]
  --force              [ Force removal (global for remove actions) ]
--list-containers      [ List containers ]
  --all                [ Show all containers ]
--run-container <image> [ Run container ]
  --name <name>        [ Container name ]
  --command <cmd>      [ Command to run ]
  --detach             [ Detach mode ]
  --ports <ports>      [ Ports, comma-separated host:container, e.g., 8080:80,8443:443 ]
  --volumes <vols>     [ Volumes, comma-separated host:container:mode, mode default rw ]
  --environment <env>  [ Env vars, comma-separated KEY=val ]
--stop-container <id>  [ Stop container ]
  --timeout <sec>      [ Timeout, default 10 ]
--remove-container <id>[ Remove container ]
  --force              [ Force ]
--get-container-logs <id> [ Get logs ]
  --tail <tail>        [ Tail lines, default all ]
--exec-in-container <id> [ Exec command ]
  --exec-command <cmd> [ Command, space-separated "ls -l /" ]
  --exec-detach        [ Detach exec ]
--list-volumes         [ List volumes ]
--create-volume <name> [ Create volume ]
--remove-volume <name> [ Remove volume ]
  --force              [ Force ]
--list-networks        [ List networks ]
--create-network <name>[ Create network ]
  --driver <driver>    [ Driver, default bridge ]
--remove-network <id>  [ Remove network ]
--compose-up <file>    [ Compose up ]
  --build              [ Build images ]
  --detach             [ Detach mode, default true ]
--compose-down <file>  [ Compose down ]
--compose-ps <file>    [ Compose ps ]
--compose-logs <file>  [ Compose logs ]
  --service <service>  [ Specific service ]
--init-swarm           [ Init swarm ]
  --advertise-addr <addr> [ Advertise address ]
--leave-swarm          [ Leave swarm ]
  --force              [ Force ]
--list-nodes           [ List swarm nodes ]
--list-services        [ List swarm services ]
--create-service <name>[ Create service ]
  --image <image>      [ Image for service ]
  --replicas <n>       [ Replicas, default 1 ]
  --ports <ports>      [ Ports, same as run-container ]
  --mounts <mounts>    [ Mounts, comma-separated source:target:mode ]
--remove-service <id>  [ Remove service ]

Example:
container_manager.py --manager docker --pull-image nginx --tag latest --list-containers --all --log-file /path/to/log.log
"""
    )


def container_manager(argv):
    parser = argparse.ArgumentParser(
        description="Container Manager: A tool to manage containers with Docker, Podman, and Docker Swarm!"
    )
    parser.add_argument("-s", "--silent", action="store_true", help="Suppress output")
    parser.add_argument(
        "-m",
        "--manager",
        type=str,
        default=None,
        help="Container manager type: docker, podman, swarm (default: auto-detect)",
    )
    parser.add_argument("--log-file", type=str, default=None, help="Path to log file")
    parser.add_argument("--get-version", action="store_true", help="Get version info")
    parser.add_argument("--get-info", action="store_true", help="Get system info")
    parser.add_argument("--list-images", action="store_true", help="List images")
    parser.add_argument("--pull-image", type=str, default=None, help="Image to pull")
    parser.add_argument("--tag", type=str, default="latest", help="Image tag")
    parser.add_argument("--platform", type=str, default=None, help="Platform")
    parser.add_argument(
        "--remove-image", type=str, default=None, help="Image to remove"
    )
    parser.add_argument("--force", action="store_true", help="Force removal")
    parser.add_argument(
        "--list-containers", action="store_true", help="List containers"
    )
    parser.add_argument("--all", action="store_true", help="Show all containers")
    parser.add_argument("--run-container", type=str, default=None, help="Image to run")
    parser.add_argument("--name", type=str, default=None, help="Container name")
    parser.add_argument("--command", type=str, default=None, help="Command to run")
    parser.add_argument("--detach", action="store_true", help="Detach mode")
    parser.add_argument("--ports", type=str, default=None, help="Port mappings")
    parser.add_argument("--volumes", type=str, default=None, help="Volume mappings")
    parser.add_argument(
        "--environment", type=str, default=None, help="Environment vars"
    )
    parser.add_argument(
        "--stop-container", type=str, default=None, help="Container to stop"
    )
    parser.add_argument("--timeout", type=int, default=10, help="Timeout in seconds")
    parser.add_argument(
        "--remove-container", type=str, default=None, help="Container to remove"
    )
    parser.add_argument(
        "--get-container-logs", type=str, default=None, help="Container logs"
    )
    parser.add_argument("--tail", type=str, default="all", help="Tail lines")
    parser.add_argument(
        "--exec-in-container", type=str, default=None, help="Container to exec"
    )
    parser.add_argument("--exec-command", type=str, default=None, help="Exec command")
    parser.add_argument("--exec-detach", action="store_true", help="Detach exec")
    parser.add_argument("--list-volumes", action="store_true", help="List volumes")
    parser.add_argument(
        "--create-volume", type=str, default=None, help="Volume to create"
    )
    parser.add_argument(
        "--remove-volume", type=str, default=None, help="Volume to remove"
    )
    parser.add_argument("--list-networks", action="store_true", help="List networks")
    parser.add_argument(
        "--create-network", type=str, default=None, help="Network to create"
    )
    parser.add_argument("--driver", type=str, default="bridge", help="Network driver")
    parser.add_argument(
        "--remove-network", type=str, default=None, help="Network to remove"
    )
    parser.add_argument("--compose-up", type=str, default=None, help="Compose file up")
    parser.add_argument("--build", action="store_true", help="Build images")
    parser.add_argument(
        "--compose-detach", action="store_true", default=True, help="Detach compose"
    )
    parser.add_argument(
        "--compose-down", type=str, default=None, help="Compose file down"
    )
    parser.add_argument("--compose-ps", type=str, default=None, help="Compose ps")
    parser.add_argument("--compose-logs", type=str, default=None, help="Compose logs")
    parser.add_argument("--service", type=str, default=None, help="Specific service")
    parser.add_argument("--init-swarm", action="store_true", help="Init swarm")
    parser.add_argument(
        "--advertise-addr", type=str, default=None, help="Advertise address"
    )
    parser.add_argument("--leave-swarm", action="store_true", help="Leave swarm")
    parser.add_argument("--list-nodes", action="store_true", help="List swarm nodes")
    parser.add_argument(
        "--list-services", action="store_true", help="List swarm services"
    )
    parser.add_argument(
        "--create-service", type=str, default=None, help="Service to create"
    )
    parser.add_argument("--image", type=str, default=None, help="Service image")
    parser.add_argument("--replicas", type=int, default=1, help="Replicas")
    parser.add_argument("--mounts", type=str, default=None, help="Mounts")
    parser.add_argument(
        "--remove-service", type=str, default=None, help="Service to remove"
    )
    parser.add_argument("-h", "--help", action="store_true", help="Show help")

    args = parser.parse_args(argv)

    if args.help:
        usage()
        sys.exit(0)

    get_version = args.get_version
    get_info = args.get_info
    list_images = args.list_images
    pull_image = args.pull_image is not None
    pull_image_str = args.pull_image
    tag = args.tag
    platform = args.platform
    remove_image = args.remove_image is not None
    remove_image_str = args.remove_image
    force = args.force
    list_containers = args.list_containers
    all_containers = args.all
    run_container = args.run_container is not None
    run_image = args.run_container
    name = args.name
    command = args.command
    detach = args.detach
    ports_str = args.ports
    volumes_str = args.volumes
    environment_str = args.environment
    stop_container = args.stop_container is not None
    stop_container_id = args.stop_container
    timeout = args.timeout
    remove_container = args.remove_container is not None
    remove_container_id = args.remove_container
    get_container_logs = args.get_container_logs is not None
    container_logs_id = args.get_container_logs
    tail = args.tail
    exec_in_container = args.exec_in_container is not None
    exec_container_id = args.exec_in_container
    exec_command = args.exec_command
    exec_detach = args.exec_detach
    list_volumes = args.list_volumes
    create_volume = args.create_volume is not None
    create_volume_name = args.create_volume
    remove_volume = args.remove_volume is not None
    remove_volume_name = args.remove_volume
    list_networks = args.list_networks
    create_network = args.create_network is not None
    create_network_name = args.create_network
    driver = args.driver
    remove_network = args.remove_network is not None
    remove_network_id = args.remove_network
    compose_up = args.compose_up is not None
    compose_up_file = args.compose_up
    compose_build = args.build
    compose_detach = args.compose_detach
    compose_down = args.compose_down is not None
    compose_down_file = args.compose_down
    compose_ps = args.compose_ps is not None
    compose_ps_file = args.compose_ps
    compose_logs = args.compose_logs is not None
    compose_logs_file = args.compose_logs
    compose_service = args.service
    init_swarm = args.init_swarm
    advertise_addr = args.advertise_addr
    leave_swarm = args.leave_swarm
    list_nodes = args.list_nodes
    list_services = args.list_services
    create_service = args.create_service is not None
    create_service_name = args.create_service
    service_image = args.image
    replicas = args.replicas
    mounts_str = args.mounts
    remove_service = args.remove_service is not None
    remove_service_id = args.remove_service
    manager_type = args.manager
    silent = args.silent
    log_file = args.log_file

    manager = create_manager(manager_type, silent, log_file)

    if get_version:
        print(json.dumps(manager.get_version(), indent=2))

    if get_info:
        print(json.dumps(manager.get_info(), indent=2))

    if list_images:
        print(json.dumps(manager.list_images(), indent=2))

    if pull_image:
        if not pull_image_str:
            raise ValueError("Image required for pull-image")
        print(json.dumps(manager.pull_image(pull_image_str, tag, platform), indent=2))

    if remove_image:
        if not remove_image_str:
            raise ValueError("Image required for remove-image")
        print(json.dumps(manager.remove_image(remove_image_str, force), indent=2))

    if list_containers:
        print(json.dumps(manager.list_containers(all_containers), indent=2))

    if run_container:
        if not run_image:
            raise ValueError("Image required for run-container")
        ports = None
        if ports_str:
            ports = {}
            for p in ports_str.split(","):
                host, cont = p.split(":")
                ports[cont + "/tcp"] = host
        volumes = None
        if volumes_str:
            volumes = {}
            for v in volumes_str.split(","):
                parts = v.split(":")
                host = parts[0]
                cont = parts[1]
                mode = parts[2] if len(parts) > 2 else "rw"
                volumes[host] = {"bind": cont, "mode": mode}
        env = None
        if environment_str:
            env = dict(e.split("=") for e in environment_str.split(","))
        print(
            json.dumps(
                manager.run_container(
                    run_image, name, command, detach, ports, volumes, env
                ),
                indent=2,
            )
        )

    if stop_container:
        if not stop_container_id:
            raise ValueError("Container ID required for stop-container")
        print(json.dumps(manager.stop_container(stop_container_id, timeout), indent=2))

    if remove_container:
        if not remove_container_id:
            raise ValueError("Container ID required for remove-container")
        print(
            json.dumps(manager.remove_container(remove_container_id, force), indent=2)
        )

    if get_container_logs:
        if not container_logs_id:
            raise ValueError("Container ID required for get-container-logs")
        print(manager.get_container_logs(container_logs_id, tail))

    if exec_in_container:
        if not exec_container_id:
            raise ValueError("Container ID required for exec-in-container")
        cmd_list = exec_command.split() if exec_command else []
        print(
            json.dumps(
                manager.exec_in_container(exec_container_id, cmd_list, exec_detach),
                indent=2,
            )
        )

    if list_volumes:
        print(json.dumps(manager.list_volumes(), indent=2))

    if create_volume:
        if not create_volume_name:
            raise ValueError("Name required for create-volume")
        print(json.dumps(manager.create_volume(create_volume_name), indent=2))

    if remove_volume:
        if not remove_volume_name:
            raise ValueError("Name required for remove-volume")
        print(json.dumps(manager.remove_volume(remove_volume_name, force), indent=2))

    if list_networks:
        print(json.dumps(manager.list_networks(), indent=2))

    if create_network:
        if not create_network_name:
            raise ValueError("Name required for create-network")
        print(json.dumps(manager.create_network(create_network_name, driver), indent=2))

    if remove_network:
        if not remove_network_id:
            raise ValueError("ID required for remove-network")
        print(json.dumps(manager.remove_network(remove_network_id), indent=2))

    if compose_up:
        if not compose_up_file:
            raise ValueError("File required for compose-up")
        print(manager.compose_up(compose_up_file, compose_detach, compose_build))

    if compose_down:
        if not compose_down_file:
            raise ValueError("File required for compose-down")
        print(manager.compose_down(compose_down_file))

    if compose_ps:
        if not compose_ps_file:
            raise ValueError("File required for compose-ps")
        print(manager.compose_ps(compose_ps_file))

    if compose_logs:
        if not compose_logs_file:
            raise ValueError("File required for compose-logs")
        print(manager.compose_logs(compose_logs_file, compose_service))

    if init_swarm:
        print(json.dumps(manager.init_swarm(advertise_addr), indent=2))

    if leave_swarm:
        print(json.dumps(manager.leave_swarm(force), indent=2))

    if list_nodes:
        print(json.dumps(manager.list_nodes(), indent=2))

    if list_services:
        print(json.dumps(manager.list_services(), indent=2))

    if create_service:
        if not create_service_name:
            raise ValueError("Name required for create-service")
        if not service_image:
            raise ValueError("Image required for create-service")
        ports = None
        if ports_str:
            ports = {}
            for p in ports_str.split(","):
                host, cont = p.split(":")
                ports[cont + "/tcp"] = host
        mounts = None
        if mounts_str:
            mounts = mounts_str.split(",")
        print(
            json.dumps(
                manager.create_service(
                    create_service_name, service_image, replicas, ports, mounts
                ),
                indent=2,
            )
        )

    if remove_service:
        if not remove_service_id:
            raise ValueError("ID required for remove-service")
        print(json.dumps(manager.remove_service(remove_service_id), indent=2))

    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    container_manager(sys.argv[1:])
