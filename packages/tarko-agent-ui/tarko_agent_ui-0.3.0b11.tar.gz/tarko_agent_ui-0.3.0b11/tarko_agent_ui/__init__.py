#!/usr/bin/env python3

"""Tarko Web UI SDK for managing static assets from @tarko/agent-ui-builder."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from ._static_version import STATIC_ASSETS_PACKAGE, STATIC_ASSETS_VERSION
except ImportError:
    # Fallback if version file doesn't exist (development mode)
    STATIC_ASSETS_VERSION = "unknown"
    STATIC_ASSETS_PACKAGE = "@tarko/agent-ui-builder"


__version__ = "0.3.0b11"
__all__ = ["get_static_path", "get_static_version", "get_agent_ui_html"]


def get_static_path() -> str:
    """Returns absolute path to bundled static assets.

    Raises:
        FileNotFoundError: When assets are missing or incomplete.
    """
    package_dir = Path(__file__).parent
    static_dir = package_dir / "static"

    if not static_dir.exists():
        raise FileNotFoundError(
            f"Static assets not found at {static_dir}. "
            "This package may not have been built properly. "
            "Please run: python scripts/build_assets.py"
        )

    # Verify essential files exist
    index_file = static_dir / "index.html"
    if not index_file.exists():
        raise FileNotFoundError(
            f"index.html not found in {static_dir}. "
            "Static assets may be incomplete. "
            "Please run: python scripts/build_assets.py"
        )

    return str(static_dir.absolute())


def get_static_version() -> dict:
    """Returns version and package information for bundled assets."""
    return {
        "version": STATIC_ASSETS_VERSION,
        "package": STATIC_ASSETS_PACKAGE,
        "sdk_version": __version__,
    }


def inject_env_variables(
    html_content: str, base_url: str = "", ui_config: Optional[Dict[str, Any]] = None
) -> str:
    """Injects environment variables into HTML head section.

    Args:
        html_content: The HTML content to modify
        base_url: Agent API base URL (defaults to empty string)
        ui_config: UI configuration object (defaults to empty dict)

    Returns:
        Modified HTML content with injected environment variables

    Raises:
        ValueError: If HTML content doesn't contain a valid head section
    """
    if ui_config is None:
        ui_config = {}

    script_tag = f"""<script>
      window.AGENT_BASE_URL = {json.dumps(base_url)};
      window.AGENT_WEB_UI_CONFIG = {json.dumps(ui_config)};
      console.log("Agent: Using API baseURL:", window.AGENT_BASE_URL);
    </script>"""

    head_pattern = r"(<head[^>]*>)"
    match = re.search(head_pattern, html_content, re.IGNORECASE)

    if not match:
        raise ValueError("HTML content must contain a valid <head> section")

    injection_point = match.end()

    modified_html = (
        html_content[:injection_point]
        + "\n    "
        + script_tag
        + "\n"
        + html_content[injection_point:]
    )

    return modified_html


def get_agent_ui_html(
    base_url: str = "", ui_config: Optional[Dict[str, Any]] = None
) -> str:
    """Returns configured Agent UI HTML content.

    Args:
        base_url: Agent API base URL (defaults to empty string)
        ui_config: UI configuration object (defaults to empty dict)

    Returns:
        HTML content with injected environment variables

    Raises:
        FileNotFoundError: When static assets are missing
        ValueError: If HTML content doesn't contain a valid head section
    """
    static_path = get_static_path()
    index_file = Path(static_path) / "index.html"

    if not index_file.exists():
        raise FileNotFoundError("index.html not found in static assets")

    html_content = index_file.read_text(encoding="utf-8")
    return inject_env_variables(
        html_content=html_content, base_url=base_url, ui_config=ui_config
    )
