import os
from jinja2 import Template
from rich.prompt import Prompt, Confirm

from pawnstack.log import AppLogger
from pawnstack.utils.file import check_file_overwrite, write_file
from pawnstack.output import print_syntax

# Initialize a logger for this module
logger = AppLogger().get_logger("pawnstack.docker.compose")


class DockerComposeBuilder:
    """
    A builder class for generating Docker Compose YAML files.

    This class guides the user through a series of prompts to gather information
    required to generate a Docker Compose configuration.

    :param project_name: The name of the Docker Compose project.
    :type project_name: str
    """

    def __init__(self, project_name="my_docker_app"):
        self.project_name = project_name
        self.cwd = os.getcwd()
        self.answers = {"services": {}}
        logger.info(f"Docker Compose project directory: {self.cwd}")

    # Template content for docker-compose.yml
    _DOCKER_COMPOSE_TEMPLATE = """
version: '3.8'

services:
{% for service_name, service_data in services.items() %}
  {{ service_name }}:
    image: {{ service_data.image }}
{% if service_data.ports %}
    ports:
{% for port in service_data.ports %}
      - "{{ port }}"
{% endfor %}
{% endif %}
{% if service_data.volumes %}
    volumes:
{% for volume in service_data.volumes %}
      - "{{ volume }}"
{% endfor %}
{% endif %}
{% if service_data.environment %}
    environment:
{% for env_var in service_data.environment %}
      - "{{ env_var }}"
{% endfor %}
{% endif %}
{% endfor %}
"""

    def _get_user_input(self):
        """
        Gathers user input for Docker Compose configuration using rich prompts.
        """
        self.answers['project_name'] = Prompt.ask(
            "Enter Docker Compose project name",
            default=self.project_name
        )

        while True:
            service_name = Prompt.ask("Enter service name (e.g., web, db) or leave empty to finish")
            if not service_name:
                break

            image = Prompt.ask(f"Enter image for {service_name} (e.g., nginx:latest)")
            ports = Prompt.ask(f"Enter ports for {service_name} (e.g., 80:80, 443:443, comma-separated)", default="")
            volumes = Prompt.ask(f"Enter volumes for {service_name} (e.g., ./data:/app/data, comma-separated)", default="")
            environment = Prompt.ask(f"Enter environment variables for {service_name} (e.g., KEY=VALUE, comma-separated)", default="")

            self.answers["services"][service_name] = {
                "image": image,
                "ports": [p.strip() for p in ports.split(',')] if ports else [],
                "volumes": [v.strip() for v in volumes.split(',')] if volumes else [],
                "environment": [e.strip() for e in environment.split(',')] if environment else [],
            }
            logger.info(f"Service '{service_name}' added.")

    def generate(self):
        """
        Generates the Docker Compose YAML file based on user input and a template.
        """
        self._get_user_input()

        template = Template(self._DOCKER_COMPOSE_TEMPLATE)

        rendered_content = template.render(**self.answers)
        output_filename = os.path.join(self.cwd, "docker-compose.yml")

        if not check_file_overwrite(filename=output_filename):
            logger.warning("Docker Compose file generation cancelled by user.")
            return None

        write_file(filename=output_filename, data=rendered_content, mode="w", encoding="utf-8")
        logger.info(f"Successfully generated Docker Compose file at: {output_filename}")

        logger.info("Generated Docker Compose content:")
        print_syntax(rendered_content, language="yaml")

        return output_filename
