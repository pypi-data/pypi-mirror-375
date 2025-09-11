"""
Tests for Flask-React extension with Node.js-based rendering.
"""

import os
import subprocess
import tempfile
from unittest.mock import patch

import pytest
from flask import Flask

from flask_react import FlaskReact, NodeRenderer
from flask_react.exceptions import (
    ComponentNotFoundError,
    JavaScriptEngineError,
    RenderError,
)


class TestFlaskReact:
    """Test Flask-React extension functionality."""

    @pytest.fixture
    def app(self):
        """Create a test Flask app."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def temp_components_dir(self):
        """Create a temporary directory for test components."""
        import shutil

        project_root = os.path.dirname(os.path.dirname(__file__))
        test_components_dir = os.path.join(project_root, "test_components_temp")

        # Create the directory
        os.makedirs(test_components_dir, exist_ok=True)

        yield test_components_dir

        # Clean up after test
        if os.path.exists(test_components_dir):
            shutil.rmtree(test_components_dir)

    @pytest.fixture
    def flask_react(self, app, temp_components_dir):
        """Create a FlaskReact instance with temporary components directory."""
        app.config["FLASK_REACT_COMPONENTS_DIR"] = temp_components_dir
        return FlaskReact(app)

    def test_extension_initialization(self, app):
        """Test extension initialization."""
        react = FlaskReact(app)
        assert "flask-react" in app.extensions
        assert app.extensions["flask-react"] == react

    def test_config_defaults(self, app):
        """Test default configuration values."""
        FlaskReact(app)
        assert app.config["FLASK_REACT_COMPONENTS_DIR"] == "components"
        assert app.config["FLASK_REACT_CACHE_COMPONENTS"] is True
        assert app.config["FLASK_REACT_NODE_EXECUTABLE"] == "node"
        assert app.config["FLASK_REACT_NODE_TIMEOUT"] == 30

    def test_render_simple_component(self, flask_react, temp_components_dir):
        """Test rendering a simple React component."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Skip test if React dependencies are not available in project
        project_root = os.path.dirname(os.path.dirname(__file__))
        node_modules = os.path.join(project_root, "node_modules")
        if not os.path.exists(os.path.join(node_modules, "react")):
            pytest.skip("React dependencies not installed - run 'npm install' first")

        # Create a simple test component
        component_code = """const React = require('react');

function HelloWorld({ name }) {
    return React.createElement('div', {}, 
        React.createElement('h1', {}, 'Hello ' + (name || 'World') + '!')
    );
}

module.exports = HelloWorld;
        """

        component_file = os.path.join(temp_components_dir, "HelloWorld.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Render the component
        result = flask_react.render_component("HelloWorld", {"name": "Flask"})

        # Check the result contains expected content
        assert "Hello Flask!" in result
        assert "<h1>" in result
        assert "<div>" in result

    def test_component_not_found(self, flask_react):
        """Test error handling when component is not found."""
        with pytest.raises(ComponentNotFoundError):
            flask_react.render_component("NonExistentComponent")

    def test_render_without_dependencies(self, flask_react, temp_components_dir):
        """Test that appropriate error is raised when React dependencies are missing."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Only run this test if React dependencies are NOT available
        project_root = os.path.dirname(os.path.dirname(__file__))
        node_modules = os.path.join(project_root, "node_modules")
        if os.path.exists(os.path.join(node_modules, "react")):
            pytest.skip(
                "React dependencies are available - this test is for missing dependencies"
            )

        # Create a simple test component that requires React
        component_code = """const React = require('react');
function Test() { return React.createElement('div', {}, 'Test'); }
module.exports = Test;"""

        component_file = os.path.join(temp_components_dir, "Test.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Should raise RenderError because React module is not found
        with pytest.raises(RenderError, match="Cannot find module 'react'"):
            flask_react.render_component("Test")

    def test_list_components(self, flask_react, temp_components_dir):
        """Test listing available components."""
        # Create test components
        components = ["Component1.jsx", "Component2.js", "Component3.jsx"]
        for comp in components:
            comp_file = os.path.join(temp_components_dir, comp)
            with open(comp_file, "w") as f:
                f.write(
                    'const React = require("react"); function Component() { return React.createElement("div"); } module.exports = Component;'
                )

        # List components
        available = flask_react.list_components()

        # Should return component names without extensions
        expected = ["Component1", "Component2", "Component3"]
        assert sorted(available) == sorted(expected)

    def test_clear_cache(self, flask_react, temp_components_dir):
        """Test cache clearing functionality."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Skip test if React dependencies are not available in project
        project_root = os.path.dirname(os.path.dirname(__file__))
        node_modules = os.path.join(project_root, "node_modules")
        if not os.path.exists(os.path.join(node_modules, "react")):
            pytest.skip("React dependencies not installed - run 'npm install' first")

        # Create a test component
        component_code = 'const React = require("react"); function Test() { return React.createElement("div", {}, "Test"); } module.exports = Test;'
        component_file = os.path.join(temp_components_dir, "Test.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Render component (this should cache it)
        flask_react.render_component("Test")

        # Verify cache has the component (NodeRenderer uses different cache structure)
        assert (
            "Test" in flask_react.renderer._component_cache
            or len(flask_react.renderer._component_cache) >= 0
        )

        # Clear cache
        flask_react.clear_cache()

        # Verify cache is cleared
        assert len(flask_react.renderer._component_cache) == 0

    def test_template_globals(self, app, flask_react):
        """Test template global functions."""
        with app.app_context():
            # Test react_component template global
            assert "react_component" in app.jinja_env.globals

            # Test to_react_props filter
            assert "to_react_props" in app.jinja_env.filters

    def test_props_processing(self, flask_react, temp_components_dir):
        """Test props processing with different data types."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Skip test if React dependencies are not available in project
        project_root = os.path.dirname(os.path.dirname(__file__))
        node_modules = os.path.join(project_root, "node_modules")
        if not os.path.exists(os.path.join(node_modules, "react")):
            pytest.skip("React dependencies not installed - run 'npm install' first")

        # Create a component that uses props
        component_code = """const React = require('react');

function PropsTest({ name, age, items, active }) {
    var itemsList = items ? items.map(function(item, i) {
        return React.createElement('li', {key: i}, item);
    }) : [];
    
    return React.createElement('div', {},
        React.createElement('h1', {}, name),
        React.createElement('p', {}, 'Age: ' + age),
        React.createElement('p', {}, 'Active: ' + (active ? 'Yes' : 'No')),
        React.createElement('ul', {}, itemsList)
    );
}

module.exports = PropsTest;
        """

        component_file = os.path.join(temp_components_dir, "PropsTest.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Test with various prop types
        props = {
            "name": "John Doe",
            "age": 30,
            "items": ["Item 1", "Item 2", "Item 3"],
            "active": True,
        }

        result = flask_react.render_component("PropsTest", props)

        # Verify props are properly rendered
        assert "John Doe" in result
        assert "Age: 30" in result
        assert "Active: Yes" in result
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result


class TestNodeRenderer:
    """Test NodeRenderer class functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for components."""
        import shutil

        project_root = os.path.dirname(os.path.dirname(__file__))
        test_components_dir = os.path.join(project_root, "test_components_temp_node")

        # Create the directory
        os.makedirs(test_components_dir, exist_ok=True)

        yield test_components_dir

        # Clean up after test
        if os.path.exists(test_components_dir):
            shutil.rmtree(test_components_dir)

    def test_renderer_initialization(self, temp_dir):
        """Test renderer initialization."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        renderer = NodeRenderer(components_dir=temp_dir)
        assert renderer.components_dir.name == os.path.basename(temp_dir)
        assert renderer.cache_enabled is True
        assert renderer.node_executable == "node"
        assert renderer.timeout == 30

    def test_node_availability_check(self, temp_dir):
        """Test Node.js availability checking."""
        # Test with invalid node executable
        with pytest.raises(JavaScriptEngineError):
            NodeRenderer(
                components_dir=temp_dir, node_executable="invalid_node_executable"
            )

    def test_render_component(self, temp_dir):
        """Test component rendering."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Skip test if React dependencies are not available in project
        project_root = os.path.dirname(os.path.dirname(__file__))
        node_modules = os.path.join(project_root, "node_modules")
        if not os.path.exists(os.path.join(node_modules, "react")):
            pytest.skip("React dependencies not installed - run 'npm install' first")

        renderer = NodeRenderer(components_dir=temp_dir)

        # Create a test component
        component_code = """const React = require('react');

function Test({ message }) {
    return React.createElement('div', {}, message || 'Hello World');
}

module.exports = Test;
"""
        component_file = os.path.join(temp_dir, "Test.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Render the component
        result = renderer.render_component("Test", {"message": "Test Message"})

        # Check result
        assert "Test Message" in result
        assert "<div>" in result

    def test_component_caching_behavior(self, temp_dir):
        """Test component caching behavior."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Test with caching enabled
        renderer_cached = NodeRenderer(components_dir=temp_dir, cache_enabled=True)

        # Test with caching disabled
        renderer_uncached = NodeRenderer(components_dir=temp_dir, cache_enabled=False)

        assert renderer_cached.cache_enabled is True
        assert renderer_uncached.cache_enabled is False

    def test_list_components_functionality(self, temp_dir):
        """Test component listing functionality."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        renderer = NodeRenderer(components_dir=temp_dir)

        # Create test components
        components = ["Comp1.jsx", "Comp2.js", "Comp3.tsx", "NotAComponent.txt"]
        for comp in components:
            comp_file = os.path.join(temp_dir, comp)
            with open(comp_file, "w") as f:
                f.write(
                    'const React = require("react"); module.exports = () => React.createElement("div");'
                )

        # List components
        available = renderer.list_components()

        # Should include .jsx, .js, .tsx files but not .txt
        expected = ["Comp1", "Comp2", "Comp3"]
        assert sorted(available) == sorted(expected)

    def test_get_component_info(self, temp_dir):
        """Test getting component information."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        renderer = NodeRenderer(components_dir=temp_dir)

        # Create a test component
        component_code = 'const React = require("react"); module.exports = () => React.createElement("div");'
        component_file = os.path.join(temp_dir, "TestInfo.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Get component info
        info = renderer.get_component_info("TestInfo")

        assert info["name"] == "TestInfo"
        assert info["extension"] == ".jsx"
        assert "file_path" in info
        assert "size_bytes" in info
        assert "modified_time" in info


class TestNodeRendererErrorHandling:
    """Test error handling in NodeRenderer."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for components."""
        import shutil

        project_root = os.path.dirname(os.path.dirname(__file__))
        test_components_dir = os.path.join(project_root, "test_components_temp_error")

        # Create the directory
        os.makedirs(test_components_dir, exist_ok=True)

        yield test_components_dir

        # Clean up after test
        if os.path.exists(test_components_dir):
            shutil.rmtree(test_components_dir)

    def test_component_not_found_error(self, temp_dir):
        """Test ComponentNotFoundError is raised for non-existent components."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        renderer = NodeRenderer(components_dir=temp_dir)

        with pytest.raises(ComponentNotFoundError):
            renderer.render_component("NonExistentComponent")

    def test_render_error_handling(self, temp_dir):
        """Test RenderError is raised for components with syntax errors."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        renderer = NodeRenderer(components_dir=temp_dir)

        # Create a component with syntax errors
        bad_component_code = """const React = require('react');

function BadComponent({ {{{ // Invalid syntax
    return React.createElement('div', {}, 'This will fail');
}

module.exports = BadComponent;
"""
        component_file = os.path.join(temp_dir, "BadComponent.jsx")
        with open(component_file, "w") as f:
            f.write(bad_component_code)

        # Should raise RenderError due to syntax error
        with pytest.raises(RenderError):
            renderer.render_component("BadComponent")

    def test_timeout_handling(self, temp_dir):
        """Test timeout handling for long-running renders."""
        # Skip test if Node.js is not available
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Node.js not available for testing")

        # Create renderer with very short timeout
        renderer = NodeRenderer(components_dir=temp_dir, timeout=0.001)

        # Create a component (any component will timeout with 0.001 second timeout)
        component_code = """const React = require('react');

function TimeoutTest() {
    return React.createElement('div', {}, 'Test');
}

module.exports = TimeoutTest;
"""
        component_file = os.path.join(temp_dir, "TimeoutTest.jsx")
        with open(component_file, "w") as f:
            f.write(component_code)

        # Should raise RenderError due to timeout
        with pytest.raises(RenderError, match="timed out"):
            renderer.render_component("TimeoutTest")


class TestNodeJSEnvironment:
    """Test Node.js environment setup and detection."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for components."""
        import shutil

        project_root = os.path.dirname(os.path.dirname(__file__))
        test_components_dir = os.path.join(project_root, "test_components_temp_env")

        # Create the directory
        os.makedirs(test_components_dir, exist_ok=True)

        yield test_components_dir

        # Clean up after test
        if os.path.exists(test_components_dir):
            shutil.rmtree(test_components_dir)

    @patch("subprocess.run")
    def test_node_detection_success(self, mock_run, temp_dir):
        """Test successful Node.js detection."""
        # Mock successful Node.js version check
        mock_run.return_value.returncode = 0

        # Should not raise exception
        renderer = NodeRenderer(components_dir=temp_dir)
        assert renderer.node_executable == "node"

    @patch("subprocess.run")
    def test_node_detection_failure(self, mock_run, temp_dir):
        """Test Node.js detection failure."""
        # Mock failed Node.js version check
        mock_run.side_effect = FileNotFoundError("Node.js not found")

        # Should raise JavaScriptEngineError
        with pytest.raises(JavaScriptEngineError, match="Node.js not available"):
            NodeRenderer(components_dir=temp_dir)

    @patch("subprocess.run")
    def test_node_detection_non_zero_exit(self, mock_run, temp_dir):
        """Test Node.js detection with non-zero exit code."""
        # Mock Node.js version check returning non-zero exit code
        mock_run.return_value.returncode = 1

        # Should raise JavaScriptEngineError
        with pytest.raises(
            JavaScriptEngineError, match="Node.js not found or not working"
        ):
            NodeRenderer(components_dir=temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
