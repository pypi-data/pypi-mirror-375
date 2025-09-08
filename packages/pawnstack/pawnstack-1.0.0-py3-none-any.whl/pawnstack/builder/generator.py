import os
from jinja2 import Template
from pyfiglet import Figlet
from rich.prompt import Confirm, Prompt

from pawnstack.log import get_logger
from pawnstack.utils.file import write_file, check_file_overwrite

# Initialize a logger for this module
logger = get_logger("pawnstack.builder.generator")


def generate_banner(
    app_name: str = "default_app",
    version: str = "0.1.0",
    author: str = "Unknown author",
    description: str = "",
    font: str = "big",
) -> str:
    """
    Generate a stylized banner for a CLI application.

    :param app_name: The name of the application.
    :param version: The version of the application.
    :param author: The author of the application.
    :param description: A short description of the application.
    :param font: The font to use for the ASCII art banner (see pyfiglet for options).
    :return: A formatted banner string.

    Example:
        .. code-block:: python

            from pawnstack.builder.generator import generate_banner
            banner = generate_banner(app_name="MyApp", version="1.0")
            print(banner)
    """
    result = []
    result.append("-" * 60)

    try:
        ascii_banner = Figlet(font=font)
        result.append(ascii_banner.renderText(app_name))
    except Exception as e:
        logger.warning(f"Failed to render Figlet banner: {e}. Using plain text.")
        result.append(app_name)

    result.append(f"  Description : {description}")
    result.append(f"  Version     : {version}")
    result.append(f"  Author      : {author}")
    result.append("-" * 60)

    return "\n".join(result)


class AppGenerator:
    """
    A class to generate a skeleton for a new application from a template.

    :param app_name: The default name for the new application.
    """
    def __init__(self, app_name="new_app"):
        self.app_name = app_name
        self.cwd = os.getcwd()
        # Assuming templates are now within the pawnstack package
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.template_name = "app_with_logging.tmpl"
        self.answers = {}
        logger.info(f"Project directory set to: {self.cwd}")

    def _get_user_input(self):
        """Private method to gather user input using rich prompts."""
        questions = [
            {
                'key': 'app_name',
                'prompt': "What's your python app name?",
                'default': self.app_name,
                'type': 'input',
            },
            {
                'key': 'author',
                'prompt': "What's your name?",
                'default': os.getlogin(),
                'type': 'input',
            },
            {
                'key': 'description',
                'prompt': "Please provide a short description of this app.",
                'default': "A new application created with PawnStack.",
                'type': 'input',
            },
            {
                'key': 'use_logger',
                'prompt': "Do you want to include a logger?",
                'default': True,
                'type': 'confirm',
            },
            {
                'key': 'use_daemon',
                'prompt': "Is this a daemon process?",
                'default': False,
                'type': 'confirm',
            },
        ]

        logger.info("Please provide the following details for your new application:")
        for q in questions:
            prompt_func = Prompt.ask if q['type'] == 'input' else Confirm.ask
            self.answers[q['key']] = prompt_func(q['prompt'], default=q.get('default'))

    def generate(self):
        """
        Generates the application file from a Jinja2 template and user input.

        :return: The path to the generated file, or None on failure.
        """
        self._get_user_input()

        app_name = self.answers.get('app_name')
        if not app_name:
            logger.error("Application name cannot be empty.")
            return None

        # Generate banner content for the template
        self.answers['banner'] = generate_banner(
            app_name=app_name,
            author=self.answers.get("author"),
            description=self.answers.get("description"),
            font="rounded",
        )

        template_path = os.path.join(self.template_dir, self.template_name)
        try:
            with open(template_path) as f:
                template_content = f.read()
            template = Template(template_content)
        except FileNotFoundError:
            logger.error(f"Template file not found at {template_path}")
            return None

        rendered_content = template.render(**self.answers)
        output_filename = os.path.join(self.cwd, f"{app_name}.py")

        if not check_file_overwrite(filename=output_filename):
            logger.warning("File generation cancelled by user.")
            return None

        write_file(filename=output_filename, data=rendered_content, mode="w", encoding="utf-8")
        os.chmod(output_filename, 0o755)
        logger.info(f"Successfully generated application file at: {output_filename}")
        return output_filename
