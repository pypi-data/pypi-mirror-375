"""Jinja2 template loader."""

from importlib.resources import files
from jinja2 import Environment, BaseLoader, select_autoescape
from typing import List, Dict

# Jinja2 environment
env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(default_for_string=True),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_template(template_name: str, **context) -> str:
    """
    Render a Jinja2 template from `miya_speechless/prompts/`.

    Parameters
    ----------
    template_name (str): Filename without `.j2` extension (e.g., 'summarize').
    **context: Variables to substitute into the template.

    Returns
    -------
    str: Rendered text from the template.
    """
    template_path = files("miya_speechless.prompts").joinpath(f"{template_name}.j2")
    template_str = template_path.read_text(encoding="utf-8")
    template = env.from_string(template_str)
    return template.render(**context)


def render_messages(template_name: str, **context) -> List[Dict[str, str]]:
    """
    Render a template and return OpenAI-style message list with roles.

    Parameters
    ----------
    template_name (str): Filename without `.j2` extension (e.g., 'summarize').
    **context: Variables to substitute into the template.

    Returns
    -------
    List[Dict[str, str]]: Messages suitable for OpenAI Chat API.

    Raises
    ------
    ValueError: If the template does not contain `System:` and `User:` blocks.
    """  # noqa: DAR401
    full_text = render_template(template_name, **context)
    try:
        system_text, user_text = full_text.split("User:")
    except ValueError as e:
        raise ValueError(f"Template '{template_name}.j2' must contain 'User:'") from e

    return [
        {"role": "system", "content": system_text.replace("System:", "").strip()},
        {"role": "user", "content": user_text.strip()},
    ]
