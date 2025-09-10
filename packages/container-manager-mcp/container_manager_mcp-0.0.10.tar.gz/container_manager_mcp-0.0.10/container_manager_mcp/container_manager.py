#!/usr/bin/env python
# coding: utf-8

import sys
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import getopt
import json
import subprocess

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

    # Compose methods
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

    # Swarm methods (to be implemented only in DockerManager)
    def init_swarm(self, advertise_addr: Optional[str] = None) -> Dict:
        raise NotImplementedError("Swarm not supported")

    def leave_swarm(self, force: bool = False) -> Dict:
        raise NotImplementedError("Swarm not supported")

    def list_nodes(self) -> List[Dict]:
        raise NotImplementedError("Swarm not supported")

    def list_services(self) -> List[Dict]:
        raise NotImplementedError("Swarm not supported")

    def create_service(
        self,
        name: str,
        image: str,
        replicas: int = 1,
        ports: Optional[Dict[str, str]] = None,
        mounts: Optional[List[str]] = None,
    ) -> Dict:
        raise NotImplementedError("Swarm not supported")

    def remove_service(self, service_id: str) -> Dict:
        raise NotImplementedError("Swarm not supported")


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

    def get_version(self) -> Dict:
        params = {}
        try:
            result = self.client.version()
            self.log_action("get_version", params, result)
            return result
        except Exception as e:
            self.log_action("get_version", params, error=e)
            raise RuntimeError(f"Failed to get version: {str(e)}")

    def get_info(self) -> Dict:
        params = {}
        try:
            result = self.client.info()
            self.log_action("get_info", params, result)
            return result
        except Exception as e:
            self.log_action("get_info", params, error=e)
            raise RuntimeError(f"Failed to get info: {str(e)}")

    def list_images(self) -> List[Dict]:
        params = {}
        try:
            images = self.client.images.list()
            result = [img.attrs for img in images]
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
            result = img.attrs
            self.log_action("pull_image", params, result)
            return result
        except Exception as e:
            self.log_action("pull_image", params, error=e)
            raise RuntimeError(f"Failed to pull image: {str(e)}")

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

    def list_containers(self, all: bool = False) -> List[Dict]:
        params = {"all": all}
        try:
            containers = self.client.containers.list(all=all)
            result = [c.attrs for c in containers]
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
            result = (
                container.attrs if detach else {"output": container.decode("utf-8")}
            )
            self.log_action("run_container", params, result)
            return result
        except Exception as e:
            self.log_action("run_container", params, error=e)
            raise RuntimeError(f"Failed to run container: {str(e)}")

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
            self.log_action("get_container_logs", params, logs)
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
                "output": output.decode("utf-8") if output else None,
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
            result = {"volumes": [v.attrs for v in volumes]}
            self.log_action("list_volumes", params, result)
            return result
        except Exception as e:
            self.log_action("list_volumes", params, error=e)
            raise RuntimeError(f"Failed to list volumes: {str(e)}")

    def create_volume(self, name: str) -> Dict:
        params = {"name": name}
        try:
            volume = self.client.volumes.create(name=name)
            result = volume.attrs
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

    def list_networks(self) -> List[Dict]:
        params = {}
        try:
            networks = self.client.networks.list()
            result = [net.attrs for net in networks]
            self.log_action("list_networks", params, result)
            return result
        except Exception as e:
            self.log_action("list_networks", params, error=e)
            raise RuntimeError(f"Failed to list networks: {str(e)}")

    def create_network(self, name: str, driver: str = "bridge") -> Dict:
        params = {"name": name, "driver": driver}
        try:
            network = self.client.networks.create(name, driver=driver)
            result = network.attrs
            self.log_action("create_network", params, result)
            return result
        except Exception as e:
            self.log_action("create_network", params, error=e)
            raise RuntimeError(f"Failed to create network: {str(e)}")

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
            result = [node.attrs for node in nodes]
            self.log_action("list_nodes", params, result)
            return result
        except Exception as e:
            self.log_action("list_nodes", params, error=e)
            raise RuntimeError(f"Failed to list nodes: {str(e)}")

    def list_services(self) -> List[Dict]:
        params = {}
        try:
            services = self.client.services.list()
            result = [service.attrs for service in services]
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
            target_ports = [docker.types.EndpointSpec(ports=ports)] if ports else None
            service = self.client.services.create(
                image,
                name=name,
                mode=mode,
                mounts=mounts,
                endpoint_spec=target_ports[0] if target_ports else None,
            )
            result = service.attrs
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
    def __init__(self, silent: bool = False, log_file: str = None):
        super().__init__(silent, log_file)
        if PodmanClient is None:
            raise ImportError("Please install podman-py: pip install podman")
        try:
            self.client = PodmanClient()
        except PodmanError as e:
            self.logger.error(f"Failed to connect to Podman daemon: {str(e)}")
            raise RuntimeError(f"Failed to connect to Podman: {str(e)}")

    def get_version(self) -> Dict:
        params = {}
        try:
            result = self.client.version()
            self.log_action("get_version", params, result)
            return result
        except Exception as e:
            self.log_action("get_version", params, error=e)
            raise RuntimeError(f"Failed to get version: {str(e)}")

    def get_info(self) -> Dict:
        params = {}
        try:
            result = self.client.info()
            self.log_action("get_info", params, result)
            return result
        except Exception as e:
            self.log_action("get_info", params, error=e)
            raise RuntimeError(f"Failed to get info: {str(e)}")

    def list_images(self) -> List[Dict]:
        params = {}
        try:
            images = self.client.images.list()
            result = [img.attrs for img in images]
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
            result = img[0].attrs if isinstance(img, list) else img.attrs
            self.log_action("pull_image", params, result)
            return result
        except Exception as e:
            self.log_action("pull_image", params, error=e)
            raise RuntimeError(f"Failed to pull image: {str(e)}")

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

    def list_containers(self, all: bool = False) -> List[Dict]:
        params = {"all": all}
        try:
            containers = self.client.containers.list(all=all)
            result = [c.attrs for c in containers]
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
            result = (
                container.attrs if detach else {"output": container.decode("utf-8")}
            )
            self.log_action("run_container", params, result)
            return result
        except Exception as e:
            self.log_action("run_container", params, error=e)
            raise RuntimeError(f"Failed to run container: {str(e)}")

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
            self.log_action("get_container_logs", params, logs)
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
                "output": output.decode("utf-8") if output else None,
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
            result = {"volumes": [v.attrs for v in volumes]}
            self.log_action("list_volumes", params, result)
            return result
        except Exception as e:
            self.log_action("list_volumes", params, error=e)
            raise RuntimeError(f"Failed to list volumes: {str(e)}")

    def create_volume(self, name: str) -> Dict:
        params = {"name": name}
        try:
            volume = self.client.volumes.create(name=name)
            result = volume.attrs
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

    def list_networks(self) -> List[Dict]:
        params = {}
        try:
            networks = self.client.networks.list()
            result = [net.attrs for net in networks]
            self.log_action("list_networks", params, result)
            return result
        except Exception as e:
            self.log_action("list_networks", params, error=e)
            raise RuntimeError(f"Failed to list networks: {str(e)}")

    def create_network(self, name: str, driver: str = "bridge") -> Dict:
        params = {"name": name, "driver": driver}
        try:
            network = self.client.networks.create(name, driver=driver)
            result = network.attrs
            self.log_action("create_network", params, result)
            return result
        except Exception as e:
            self.log_action("create_network", params, error=e)
            raise RuntimeError(f"Failed to create network: {str(e)}")

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


def create_manager(
    manager_type: str, silent: bool = False, log_file: str = None
) -> ContainerManagerBase:
    if manager_type.lower() == "docker" or manager_type.lower() == "swarm":
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
-m | --manager <type>  [ docker, podman, swarm; default: docker ]
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
    get_version = False
    get_info = False
    list_images = False
    pull_image = False
    pull_image_str = None
    tag = "latest"
    platform = None
    remove_image = False
    remove_image_str = None
    force = False
    list_containers = False
    all_containers = False
    run_container = False
    run_image = None
    name = None
    command = None
    detach = False
    ports_str = None
    volumes_str = None
    environment_str = None
    stop_container = False
    stop_container_id = None
    timeout = 10
    remove_container = False
    remove_container_id = None
    get_container_logs = False
    container_logs_id = None
    tail = "all"
    exec_in_container = False
    exec_container_id = None
    exec_command = None
    exec_detach = False
    list_volumes = False
    create_volume = False
    create_volume_name = None
    remove_volume = False
    remove_volume_name = None
    list_networks = False
    create_network = False
    create_network_name = None
    driver = "bridge"
    remove_network = False
    remove_network_id = None
    compose_up = False
    compose_up_file = None
    compose_build = False
    compose_detach = True
    compose_down = False
    compose_down_file = None
    compose_ps = False
    compose_ps_file = None
    compose_logs = False
    compose_logs_file = None
    compose_service = None
    init_swarm = False
    advertise_addr = None
    leave_swarm = False
    list_nodes = False
    list_services = False
    create_service = False
    create_service_name = None
    service_image = None
    replicas = 1
    mounts_str = None
    remove_service = False
    remove_service_id = None
    manager_type = "docker"
    silent = False
    log_file = None

    try:
        opts, _ = getopt.getopt(
            argv,
            "hsm:",
            [
                "help",
                "silent",
                "manager=",
                "log-file=",
                "get-version",
                "get-info",
                "list-images",
                "pull-image=",
                "tag=",
                "platform=",
                "remove-image=",
                "force",
                "list-containers",
                "all",
                "run-container=",
                "name=",
                "command=",
                "detach",
                "ports=",
                "volumes=",
                "environment=",
                "stop-container=",
                "timeout=",
                "remove-container=",
                "get-container-logs=",
                "tail=",
                "exec-in-container=",
                "exec-command=",
                "exec-detach",
                "list-volumes",
                "create-volume=",
                "remove-volume=",
                "list-networks",
                "create-network=",
                "driver=",
                "remove-network=",
                "compose-up=",
                "build",
                "compose-down=",
                "compose-ps=",
                "compose-logs=",
                "service=",
                "init-swarm",
                "advertise-addr=",
                "leave-swarm",
                "list-nodes",
                "list-services",
                "create-service=",
                "image=",
                "replicas=",
                "mounts=",
                "remove-service=",
            ],
        )
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--silent"):
            silent = True
        elif opt in ("-m", "--manager"):
            manager_type = arg
        elif opt == "--log-file":
            log_file = arg
        elif opt == "--get-version":
            get_version = True
        elif opt == "--get-info":
            get_info = True
        elif opt == "--list-images":
            list_images = True
        elif opt == "--pull-image":
            pull_image = True
            pull_image_str = arg
        elif opt == "--tag":
            tag = arg
        elif opt == "--platform":
            platform = arg
        elif opt == "--remove-image":
            remove_image = True
            remove_image_str = arg
        elif opt == "--force":
            force = True
        elif opt == "--list-containers":
            list_containers = True
        elif opt == "--all":
            all_containers = True
        elif opt == "--run-container":
            run_container = True
            run_image = arg
        elif opt == "--name":
            name = arg
        elif opt == "--command":
            command = arg
        elif opt == "--detach":
            detach = True
        elif opt == "--ports":
            ports_str = arg
        elif opt == "--volumes":
            volumes_str = arg
        elif opt == "--environment":
            environment_str = arg
        elif opt == "--stop-container":
            stop_container = True
            stop_container_id = arg
        elif opt == "--timeout":
            timeout = int(arg)
        elif opt == "--remove-container":
            remove_container = True
            remove_container_id = arg
        elif opt == "--get-container-logs":
            get_container_logs = True
            container_logs_id = arg
        elif opt == "--tail":
            tail = arg
        elif opt == "--exec-in-container":
            exec_in_container = True
            exec_container_id = arg
        elif opt == "--exec-command":
            exec_command = arg
        elif opt == "--exec-detach":
            exec_detach = True
        elif opt == "--list-volumes":
            list_volumes = True
        elif opt == "--create-volume":
            create_volume = True
            create_volume_name = arg
        elif opt == "--remove-volume":
            remove_volume = True
            remove_volume_name = arg
        elif opt == "--list-networks":
            list_networks = True
        elif opt == "--create-network":
            create_network = True
            create_network_name = arg
        elif opt == "--driver":
            driver = arg
        elif opt == "--remove-network":
            remove_network = True
            remove_network_id = arg
        elif opt == "--compose-up":
            compose_up = True
            compose_up_file = arg
        elif opt == "--build":
            compose_build = True
        elif opt == "--compose-down":
            compose_down = True
            compose_down_file = arg
        elif opt == "--compose-ps":
            compose_ps = True
            compose_ps_file = arg
        elif opt == "--compose-logs":
            compose_logs = True
            compose_logs_file = arg
        elif opt == "--service":
            compose_service = arg
        elif opt == "--init-swarm":
            init_swarm = True
        elif opt == "--advertise-addr":
            advertise_addr = arg
        elif opt == "--leave-swarm":
            leave_swarm = True
        elif opt == "--list-nodes":
            list_nodes = True
        elif opt == "--list-services":
            list_services = True
        elif opt == "--create-service":
            create_service = True
            create_service_name = arg
        elif opt == "--image":
            service_image = arg
        elif opt == "--replicas":
            replicas = int(arg)
        elif opt == "--mounts":
            mounts_str = arg
        elif opt == "--remove-service":
            remove_service = True
            remove_service_id = arg

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
