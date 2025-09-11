"""
Flask-React extension main class.
Provides Flask integration for server-side React component rendering.
"""

import os
from typing import Any, Dict, Optional

from flask import Flask, current_app, render_template_string, request
from jinja2 import Template

from .exceptions import FlaskReactError
from .node_renderer import NodeRenderer


class FlaskReact:
    """Main Flask-React extension class."""

    def __init__(self, app: Optional[Flask] = None):
        """
        Initialize Flask-React extension.

        Args:
            app: Flask application instance
        """
        self.app = app
        self._renderer = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """
        Initialize the extension with a Flask application.

        Args:
            app: Flask application instance
        """
        self.app = app

        # Set default configuration
        app.config.setdefault("FLASK_REACT_COMPONENTS_DIR", "components")
        app.config.setdefault("FLASK_REACT_CACHE_COMPONENTS", True)
        app.config.setdefault("FLASK_REACT_PERFORMANCE_MONITORING", app.debug)
        app.config.setdefault("FLASK_REACT_MAX_CACHE_SIZE", 100)
        app.config.setdefault("FLASK_REACT_BABEL_PRESETS", ["@babel/preset-react"])
        app.config.setdefault("FLASK_REACT_AUTO_RELOAD", app.debug)
        app.config.setdefault("FLASK_REACT_NODE_TIMEOUT", 30)
        app.config.setdefault("FLASK_REACT_NODE_EXECUTABLE", "node")
        # Initialize renderer
        self._init_renderer()

        # Add template globals and filters
        self._add_template_globals()

        # Store extension in app extensions
        app.extensions["flask-react"] = self

    def _init_renderer(self):
        """Initialize the React renderer."""
        components_dir = self.app.config["FLASK_REACT_COMPONENTS_DIR"]
        cache_enabled = self.app.config["FLASK_REACT_CACHE_COMPONENTS"]

        # Make components directory absolute if it's relative
        if not os.path.isabs(components_dir):
            components_dir = os.path.join(self.app.root_path, components_dir)

            # Node.js-based renderer
        node_executable = self.app.config["FLASK_REACT_NODE_EXECUTABLE"]
        timeout = self.app.config["FLASK_REACT_NODE_TIMEOUT"]

        self._renderer = NodeRenderer(
            components_dir=components_dir,
            cache_enabled=cache_enabled,
            node_executable=node_executable,
            timeout=timeout,
        )

    def _add_template_globals(self):
        """Add React-related functions to Jinja2 template globals."""

        @self.app.template_global()
        def react_component(component_name: str, **props):
            """
            Render a React component within a Jinja2 template.

            Usage in template:
                {{ react_component('MyComponent', name='John', age=30) }}
            """
            return self.render_component(component_name, props)

        @self.app.template_filter()
        def to_react_props(value):
            """
            Convert a Python value to React props format.

            Usage in template:
                {{ my_data | to_react_props }}
            """
            import json

            return json.dumps(value) if value is not None else "{}"

    def render_component(
        self,
        component_name: str,
        props: Optional[Dict[str, Any]] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a React component to HTML string.

        Args:
            component_name: Name of the component to render
            props: Props to pass to the component
            template_data: Additional template data for Jinja2 processing

        Returns:
            Rendered HTML string
        """
        if self._renderer is None:
            self._init_renderer()

        # Process props through Jinja2 for template-like functionality
        if template_data:
            processed_props = self._process_props_with_jinja(props or {}, template_data)
        else:
            processed_props = props or {}

        if self._renderer is None:
            raise RuntimeError("Flask-React not properly initialized")

        result = self._renderer.render_component(component_name, processed_props)
        return str(result)

    def render_template(self, component_name: str, **context) -> str:
        """
        Render a React component as a Flask template.
        Similar to Flask's render_template() but for React components.

        Args:
            component_name: Name of the component to render
            **context: Template context variables

        Returns:
            Rendered HTML string
        """
        return self.render_component(component_name, context)

    def _process_props_with_jinja(
        self, props: Dict[str, Any], template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process props using Jinja2 template engine for dynamic values.

        Args:
            props: Original props
            template_data: Template context data

        Returns:
            Processed props
        """
        import json

        processed_props = {}

        for key, value in props.items():
            if isinstance(value, str) and ("{{" in value or "{%" in value):
                # Process as Jinja2 template
                template = Template(value)
                processed_value = template.render(**template_data)

                # Try to parse as JSON if it looks like structured data
                try:
                    processed_props[key] = json.loads(processed_value)
                except (json.JSONDecodeError, ValueError):
                    processed_props[key] = processed_value
            else:
                processed_props[key] = value

        return processed_props

    def list_components(self):
        """List all available React components."""
        if self._renderer is None:
            self._init_renderer()
        return self._renderer.list_components()

    def clear_cache(self):
        """Clear the component cache."""
        if self._renderer is not None:
            self._renderer.clear_cache()

    def get_component_info(self, component_name: str):
        """Get information about a specific component."""
        if self._renderer is None:
            self._init_renderer()

        if self._renderer is None:
            raise RuntimeError("Flask-React not properly initialized")
        return self._renderer.get_component_info(component_name)

    @property
    def renderer(self):
        """Get the underlying renderer instance (NodeRenderer)."""
        if self._renderer is None:
            self._init_renderer()
        return self._renderer


# Convenience function for creating responses
def react_response(
    component_name: str,
    props: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
):
    """
    Create a Flask response with rendered React component.

    Args:
        component_name: Name of the component to render
        props: Props to pass to the component
        status_code: HTTP status code
        headers: Additional headers

    Returns:
        Flask Response object
    """
    from flask import Response

    # Get Flask-React extension instance
    flask_react = current_app.extensions.get("flask-react")
    if flask_react is None:
        raise FlaskReactError("Flask-React extension not initialized")

    # Render component
    html = flask_react.render_component(component_name, props)

    # Create response
    response = Response(html, status=status_code, mimetype="text/html")

    if headers:
        for key, value in headers.items():
            response.headers[key] = value

    return response
