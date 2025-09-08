import asyncio
import re
from functools import partial

import aiodocker
import aiometer

from pawnstack.log import get_logger

# Initialize a logger for this module
logger = get_logger("pawnstack.docker.async_client")


class AsyncDocker:
    """
    An asynchronous Docker client to manage containers and images.

    This class provides a high-level API for common Docker operations using aiodocker.
    It supports context management for proper resource handling.

    :param client_options: Dictionary of options to pass to the aiodocker.Docker client.
    :param max_at_once: Max number of concurrent tasks for batch operations.
    :param max_per_second: Max number of tasks per second for batch operations.
    """

    def __init__(self, client_options=None, max_at_once=10, max_per_second=10):
        self.client_options = client_options or {}
        self._client = None
        self.max_at_once = max_at_once
        self.max_per_second = max_per_second

    async def _get_client(self):
        """Get or create the Docker client."""
        if self._client is None:
            self._client = aiodocker.Docker(**self.client_options)
        return self._client

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Closes the Docker client session."""
        if self._client:
            client = await self._get_client()
            if hasattr(client, 'session') and client.session and not client.session.closed:
                await client.close()
                logger.debug("Docker client session closed.")
            self._client = None

    async def list_images(self, simple=True):
        """Lists all Docker images."""
        client = await self._get_client()
        images = []
        try:
            for image in await client.images.list():
                if isinstance(image.get('RepoTags'), list):
                    for tag in image['RepoTags']:
                        if simple:
                            images.append({"id": image['Id'].replace("sha256:", "")[:12], "tags": tag})
                        else:
                            images.append(image)
        except aiodocker.exceptions.DockerError as e:
            logger.error(f"Failed to list Docker images: {e}")
        return images

    async def list_containers(self, filters=None, **kwargs):
        """Lists containers, optionally filtering them."""
        containers = []
        try:
            raw_containers = await self.client.containers.list(**kwargs)
            for container in raw_containers:
                if self._filter_item(container._container, filters):
                    containers.append(container)
        except aiodocker.exceptions.DockerError as e:
            logger.error(f"Failed to list Docker containers: {e}")
        return containers

    def _filter_item(self, item, filters):
        """Helper to filter a dictionary based on regex patterns."""
        if not filters:
            return True
        for key, pattern in filters.items():
            target_value = item.get(key, "")
            if isinstance(target_value, list):
                target_value = " ".join(target_value)
            if re.fullmatch(pattern, target_value):
                return True
        return False

    async def pull_image(self, image_name):
        """Pulls a Docker image from a registry."""
        try:
            logger.info(f"Pulling image: {image_name}")
            await self.client.images.pull(image_name)
            logger.info(f"Successfully pulled image: {image_name}")
            return True
        except aiodocker.exceptions.DockerError as e:
            logger.error(f"Failed to pull image {image_name}: {e}")
            return False

    async def control_containers(self, method, filters=None, **kwargs):
        """Runs a specific method on a batch of containers."""
        containers = await self.list_containers(filters=filters, all=True)
        if not containers:
            logger.info(f"No containers found matching filters: {filters}")
            return []

        tasks = []
        for i, container in enumerate(containers):
            logger.info(f"[{i+1}/{len(containers)}] Applying '{method}' to {container.id[:12]} ({container._container.get('Name')})")
            func = getattr(container, method, None)
            if callable(func):
                tasks.append(partial(func, force=True))  # Assuming force=True for methods like delete

        if not tasks:
            return []

        results = await aiometer.run_all(tasks, max_at_once=self.max_at_once, max_per_second=self.max_per_second)
        return results


async def run_container(image, name, env=None, network_mode='host', **kwargs):
    """
    Creates and starts a single Docker container.
    """
    client = aiodocker.Docker()
    container = None
    try:
        config = {
            'Image': image,
            'Hostname': name,
            'Env': env or [],
            'NetworkMode': network_mode,
        }
        logger.info(f"Creating container '{name}' from image '{image}'")
        container = await client.containers.create_or_replace(config=config, name=name)
        await container.start()
        logger.info(f"Container '{name}' started successfully.")
        return container
    except aiodocker.exceptions.DockerError as e:
        logger.error(f"Failed to run container '{name}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error running container '{name}': {e}")
        return None
    finally:
        if client:
            try:
                await client.close()
            except Exception:
                pass  # Ignore errors when closing client
