"""
Node.js-based React renderer for Flask-React extension.
Uses Node.js subprocess to handle React SSR reliably.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ComponentNotFoundError, JavaScriptEngineError, RenderError


class NodeRenderer:
    """Handles server-side rendering of React components using Node.js."""

    def __init__(
        self,
        components_dir: str = "components",
        cache_enabled: bool = True,
        node_executable: str = "node",
        timeout: int = 30,
    ):
        """
        Initialize the Node.js-based React renderer.

        Args:
            components_dir: Directory containing React components
            cache_enabled: Whether to cache compiled components
            node_executable: Path to Node.js executable
            timeout: Timeout for Node.js processes in seconds
        """
        self.components_dir = Path(components_dir)
        self.cache_enabled = cache_enabled
        self.node_executable = node_executable
        self.timeout = timeout

        self._component_cache: Dict[str, str] = {}
        self._component_mtimes: Dict[str, float] = {}

        # Ensure Node.js is available
        self._check_node_availability()

        # Create SSR script and track if it's temporary
        self._is_temp_script = False
        self._create_ssr_script()

    def _check_node_availability(self):
        """Check if Node.js is available."""
        try:
            result = subprocess.run(
                [self.node_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise JavaScriptEngineError(
                    f"Node.js not found or not working: {self.node_executable}"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise JavaScriptEngineError(f"Node.js not available: {str(e)}")

    def _create_ssr_script(self):
        """Create or locate the Node.js SSR script."""
        # Try multiple locations for the SSR server
        possible_locations = [
            # 1. Bundled with the package (preferred)
            Path(__file__).parent / "ssr_server.js",
            # 2. In the project root (for development)
            Path(__file__).parent.parent / "ssr_server.js",
            # 3. In current working directory
            Path.cwd() / "ssr_server.js",
        ]

        for script_path in possible_locations:
            if script_path.exists():
                self.ssr_script_path = script_path
                # This is a bundled/existing script, not temporary
                self._is_temp_script = False
                return

        # Fallback: create a basic SSR script in a temporary location
        import tempfile

        temp_dir = Path(tempfile.gettempdir())
        self._create_fallback_ssr_script(temp_dir)
        # Mark this as a temporary script that should be cleaned up
        self._is_temp_script = True

    def _create_fallback_ssr_script(self, project_root):
        """Create a fallback SSR script if the main one isn't found."""
        ssr_script_content = """
const React = require('react');
const { renderToString } = require('react-dom/server');

// Get cache setting from command line arguments or default to true
const cacheEnabled = process.argv[4] === 'true' || process.argv[4] === undefined;

// Setup Babel for JSX transformation
try {
    require('@babel/register')({
        presets: ['@babel/preset-react'],
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
        cache: cacheEnabled // Respect cache configuration
    });
} catch (e) {
    console.warn('Babel not available, JSX transformation disabled:', e.message);
}

// Mock DOM globals for SSR
global.window = {};
global.document = {};
global.navigator = { userAgent: 'node' };

function requireComponent(componentPath) {
    try {
        // Clear require cache for hot reloading only if caching is disabled
        if (!cacheEnabled) {
            delete require.cache[require.resolve(componentPath)];
        }
        return require(componentPath);
    } catch (error) {
        throw new Error(`Cannot load component ${componentPath}: ${error.message}`);
    }
}

function renderComponent(componentPath, props) {
    try {
        const ComponentModule = requireComponent(componentPath);
        
        // Handle different export patterns
        let Component;
        if (typeof ComponentModule === 'function') {
            Component = ComponentModule;
        } else if (ComponentModule.default && typeof ComponentModule.default === 'function') {
            Component = ComponentModule.default;
        } else {
            throw new Error('Component must export a function or have a default export that is a function');
        }
        
        // Create React element and render
        const element = React.createElement(Component, props || {});
        const html = renderToString(element);
        
        return { 
            success: true, 
            html: html, 
            error: null 
        };
    } catch (error) {
        return {
            success: false,
            html: null,
            error: { 
                message: error.message, 
                stack: error.stack,
                component: componentPath
            }
        };
    }
}

// Handle command line arguments
// argv[2] = componentPath, argv[3] = propsJson, argv[4] = cacheEnabled
if (process.argv.length >= 3) {
    const componentPath = process.argv[2];
    const propsJson = process.argv[3] || '{}';
    
    try {
        const props = JSON.parse(propsJson);
        const result = renderComponent(componentPath, props);
        console.log(JSON.stringify(result));
        process.exit(result.success ? 0 : 1);
    } catch (parseError) {
        console.log(JSON.stringify({
            success: false,
            html: null,
            error: { 
                message: `Invalid JSON props: ${parseError.message}`,
                stack: parseError.stack
            }
        }));
        process.exit(1);
    }
}
"""

        self.ssr_script_path = project_root / "flask_react_ssr_temp.js"
        with open(self.ssr_script_path, "w", encoding="utf-8") as f:
            f.write(ssr_script_content)

    def render_component(
        self, component_name: str, props: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a React component to HTML string using Node.js.

        Args:
            component_name: Name of the component to render
            props: Props to pass to the component

        Returns:
            Rendered HTML string

        Raises:
            ComponentNotFoundError: If component file is not found
            RenderError: If rendering fails
        """
        # Find component file
        component_file = self._find_component_file(component_name)
        if component_file is None:
            raise ComponentNotFoundError(
                f"Component '{component_name}' not found in {self.components_dir}"
            )

        try:
            # Prepare command line arguments
            component_path = str(component_file.absolute())
            props_json = json.dumps(props or {})
            cache_enabled = str(self.cache_enabled).lower()

            # Run Node.js SSR script with command line arguments
            # Set working directory to project root so Node.js can find dependencies
            project_root = Path(__file__).parent.parent
            process = subprocess.run(
                [
                    self.node_executable,
                    str(self.ssr_script_path),
                    component_path,
                    props_json,
                    cache_enabled,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self.timeout,
                cwd=str(project_root),  # Set working directory
            )

            stdout = process.stdout
            stderr = process.stderr

            if process.returncode != 0:
                error_msg = stderr if stderr else "Unknown Node.js error"
                # Add more debugging information
                debug_info = f"Return code: {process.returncode}, stdout: '{stdout}', stderr: '{stderr}'"
                raise RenderError(
                    f"Node.js process failed: {error_msg}. Debug info: {debug_info}"
                )

            # Parse result
            try:
                result = json.loads(stdout)
            except json.JSONDecodeError as e:
                raise RenderError(f"Failed to parse Node.js output: {str(e)}")

            if not result.get("success"):
                error_info = result.get("error", {})
                error_msg = error_info.get("message", "Unknown rendering error")
                raise RenderError(f"Component rendering failed: {error_msg}")

            html_result = result.get("html")
            if html_result is None:
                raise RenderError("No HTML content in rendering result")
            return str(html_result)

        except subprocess.TimeoutExpired:
            raise RenderError(
                f"Component rendering timed out after {self.timeout} seconds"
            )
        except Exception as e:
            if isinstance(e, (ComponentNotFoundError, RenderError)):
                raise
            raise RenderError(
                f"Failed to render component '{component_name}': {str(e)}"
            )

    def _find_component_file(self, component_name: str) -> Optional[Path]:
        """Find component file by name."""
        # Prioritize .js files first (don't need Babel), then JSX files
        for ext in [".js", ".jsx", ".ts", ".tsx"]:
            component_file = self.components_dir / f"{component_name}{ext}"
            if component_file.exists():
                return component_file
        return None

    def list_components(self) -> list[str]:
        """List all available components."""
        if not self.components_dir.exists():
            return []

        components = []
        extensions = ["*.jsx", "*.js", "*.ts", "*.tsx"]

        for pattern in extensions:
            for file_path in self.components_dir.glob(pattern):
                if file_path.stem not in components:
                    components.append(file_path.stem)

        return sorted(components)

    def get_component_info(self, component_name: str) -> Dict[str, Any]:
        """Get information about a specific component."""
        component_file = self._find_component_file(component_name)
        if component_file is None:
            raise ComponentNotFoundError(f"Component '{component_name}' not found")

        stat = component_file.stat()
        return {
            "name": component_name,
            "file_path": str(component_file),
            "extension": component_file.suffix,
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime,
        }

    def clear_cache(self):
        """Clear component cache (Node.js handles its own caching)."""
        self._component_cache.clear()
        self._component_mtimes.clear()

    def __del__(self):
        """Clean up temporary files."""
        try:
            if (
                hasattr(self, "ssr_script_path")
                and hasattr(self, "_is_temp_script")
                and self._is_temp_script
                and self.ssr_script_path.exists()
            ):
                self.ssr_script_path.unlink()
        except:
            pass  # Ignore cleanup errors
