"""
Custom exceptions for Flask-React extension.
"""


class FlaskReactError(Exception):
    """Base exception for Flask-React related errors."""

    pass


class ComponentNotFoundError(FlaskReactError):
    """Raised when a React component cannot be found."""

    pass


class RenderError(FlaskReactError):
    """Raised when there's an error during component rendering."""

    pass


class JavaScriptEngineError(FlaskReactError):
    """Raised when there's an error with the JavaScript engine."""

    pass


class ComponentCompileError(FlaskReactError):
    """Raised when there's an error compiling a React component."""

    pass
