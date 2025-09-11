# Flask-React Extension Documentation

## Overview

Flask-React is a Flask extension that enables server-side rendering of React components with template-like functionality similar to Jinja2. It uses Node.js for fast and reliable React component rendering on the server-side.

## Features

- **Server-side React rendering**: Render React components on the server using Node.js subprocess
- **Template-like syntax**: Support for conditions, loops, and data binding like Jinja2
- **Flask integration**: Seamless integration with Flask applications
- **Component caching**: Cache compiled components for better performance
- **Props passing**: Pass data from Flask routes to React components
- **Development-friendly**: Hot reloading and error handling
- **Fast Node.js engine**: Direct Node.js subprocess for optimal performance
- **Flexible component support**: Support for .jsx, .js, .ts, .tsx files

## Installation

```bash
pip install flask-react
```

### Dependencies

- Flask >= 2.0.0
- Jinja2 >= 3.0.0
- Node.js (required for server-side rendering)

### Node.js Setup

Flask-React requires Node.js to execute React components. **Node.js is mandatory** for this extension:

**Install Node.js**:
```bash
# Download and install from https://nodejs.org/
# Verify installation:
node --version
npm --version
```

**Install React dependencies**:
The Flask-React package includes a `package.json` with all required dependencies. Simply run:
```bash
npm install
```

This will install:
- `react` and `react-dom` (for React SSR)
- `@babel/core`, `@babel/preset-react` (for JSX transformation)
- `@babel/preset-env` (for modern JavaScript features)
- `@babel/preset-typescript` (for TypeScript support)
- `@babel/register` (for runtime JSX compilation)

## Quick Start

### 1. Basic Setup

```python
from flask import Flask
from flask_react import FlaskReact

app = Flask(__name__)
react = FlaskReact(app)

# Or use init_app pattern
react = FlaskReact()
react.init_app(app)
```

### 2. Create a Component

Create a `components/` directory in your Flask app root and add a React component:

```jsx
// components/HelloWorld.jsx
function HelloWorld({ name, items }) {
    return (
        <div>
            <h1>Hello {name}!</h1>
            {items && items.length > 0 && (
                <ul>
                    {items.map((item, index) => (
                        <li key={index}>{item}</li>
                    ))}
                </ul>
            )}
        </div>
    );
}
```

### 3. Render in Flask Route

```python
@app.route('/')
def home():
    return react.render_template('HelloWorld', 
        name='Flask React',
        items=['Feature 1', 'Feature 2', 'Feature 3']
    )
```

## Setup Guide

### Complete Setup from Scratch

1. **Install Node.js**:
   ```bash
   # Visit https://nodejs.org/ and install Node.js
   # Verify installation:
   node --version  # Should show v16.0.0 or higher
   npm --version
   ```

2. **Create Flask project**:
   ```bash
   mkdir my-flask-react-app
   cd my-flask-react-app
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install flask-react flask
   ```

4. **Install Node.js dependencies**:
   ```bash
   # Copy package.json from Flask-React installation or create your own
   # If using Flask-React package.json:
   npm install
   
   # Or if creating from scratch:
   npm init -y
   npm install react react-dom @babel/core @babel/preset-react @babel/register
   ```

5. **Create project structure**:
   ```bash
   mkdir components
   mkdir templates
   touch app.py
   ```

6. **Create a basic Flask app** (`app.py`):
   ```python
   from flask import Flask
   from flask_react import FlaskReact
   
   app = Flask(__name__)
   react = FlaskReact(app)
   
   @app.route('/')
   def index():
       return react.render_component('HelloWorld', {
           'name': 'World',
           'message': 'Welcome to Flask-React!'
       })
   
   if __name__ == '__main__':
       app.run(debug=True)
   ```

7. **Create your first component** (`components/HelloWorld.jsx`):
   ```jsx
   function HelloWorld({ name, message }) {
       return (
           <div style={{ padding: '20px', textAlign: 'center' }}>
               <h1>Hello {name}!</h1>
               <p>{message}</p>
           </div>
       );
   }
   
   module.exports = HelloWorld;
   ```

8. **Run the application**:
   ```bash
   python app.py
   ```

### Troubleshooting Setup

#### Node.js Issues
- **"Node.js not found"**: Ensure Node.js is in your PATH or set explicit path:
  ```python
  app.config['FLASK_REACT_NODE_EXECUTABLE'] = '/usr/local/bin/node'  # Linux/Mac
  app.config['FLASK_REACT_NODE_EXECUTABLE'] = 'C:\\Program Files\\nodejs\\node.exe'  # Windows
  ```

- **Permission errors**: Ensure the Node.js executable has proper permissions

#### Component Issues
- **"Component not found"**: Check file names and extensions (.jsx, .js, .ts, .tsx)
- **Syntax errors**: Ensure your JSX is valid and components are properly exported

#### Babel Issues
- **JSX transformation errors**: Ensure dependencies are installed:
  ```bash
  npm install  # Installs all dependencies from package.json
  ```
- **Babel configuration**: The package.json includes proper Babel presets configuration

## Configuration

Configure Flask-React using standard Flask configuration:

```python
app.config['FLASK_REACT_COMPONENTS_DIR'] = 'components'  # Component directory
app.config['FLASK_REACT_CACHE_COMPONENTS'] = True       # Enable component caching
app.config['FLASK_REACT_NODE_EXECUTABLE'] = 'node'      # Node.js executable path
app.config['FLASK_REACT_NODE_TIMEOUT'] = 30             # Node.js process timeout (seconds)
app.config['FLASK_REACT_AUTO_RELOAD'] = app.debug       # Auto-reload in debug mode
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `FLASK_REACT_COMPONENTS_DIR` | `'components'` | Directory containing React components |
| `FLASK_REACT_CACHE_COMPONENTS` | `True` | Enable component caching (affects both Python and Node.js caching) |
| `FLASK_REACT_NODE_EXECUTABLE` | `'node'` | Path to Node.js executable |
| `FLASK_REACT_NODE_TIMEOUT` | `30` | Timeout for Node.js processes in seconds |
| `FLASK_REACT_AUTO_RELOAD` | `app.debug` | Auto-reload components in debug mode |

## Usage Examples

### Conditional Rendering

```jsx
// components/UserProfile.jsx
function UserProfile({ user, current_user, is_admin }) {
    return (
        <div>
            <h1>{user.name}</h1>
            {current_user.id === user.id && (
                <div>
                    <p>This is your profile</p>
                    <button>Edit Profile</button>
                </div>
            )}
            {is_admin && (
                <div>
                    <h2>Admin Tools</h2>
                    <button>Delete User</button>
                </div>
            )}
        </div>
    );
}
```

```python
@app.route('/user/<int:user_id>')
def user_profile(user_id):
    user = get_user(user_id)
    return react.render_template('UserProfile',
        user=user,
        current_user=g.current_user,
        is_admin=g.current_user.has_role('admin')
    )
```

### List Rendering

```jsx
// components/ProductList.jsx
function ProductList({ products, category_filter }) {
    const filtered_products = category_filter 
        ? products.filter(p => p.category === category_filter)
        : products;
    
    return (
        <div>
            <h1>Products</h1>
            {category_filter && (
                <p>Showing products in: {category_filter}</p>
            )}
            <div className="products">
                {filtered_products.map(product => (
                    <div key={product.id} className="product-card">
                        <h3>{product.name}</h3>
                        <p>${product.price}</p>
                        <span className="category">{product.category}</span>
                    </div>
                ))}
            </div>
            {filtered_products.length === 0 && (
                <p>No products found.</p>
            )}
        </div>
    );
}
```

### Form Components

```jsx
// components/ContactForm.jsx
function ContactForm({ fields, action, method }) {
    return (
        <form action={action || '/contact'} method={method || 'POST'}>
            {fields.map((field, index) => (
                <div key={index} className="form-group">
                    <label>{field.label}</label>
                    {field.type === 'textarea' ? (
                        <textarea 
                            name={field.name}
                            required={field.required}
                        />
                    ) : (
                        <input 
                            type={field.type || 'text'}
                            name={field.name}
                            required={field.required}
                        />
                    )}
                </div>
            ))}
            <button type="submit">Submit</button>
        </form>
    );
}
```

## Template Integration

### Using in Jinja2 Templates

Flask-React provides template globals for use within Jinja2 templates:

```html
<!-- templates/page.html -->
<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
</head>
<body>
    <header>
        {{ react_component('Navigation', user=current_user) }}
    </header>
    
    <main>
        {{ react_component('Content', data=page_data) }}
    </main>
    
    <footer>
        {{ react_component('Footer') }}
    </footer>
</body>
</html>
```

### Props Serialization

Use the `to_react_props` filter to serialize complex data:

```html
<div id="app" data-props="{{ my_data | to_react_props }}">
    {{ react_component('App', **my_data) }}
</div>
```

## API Reference

### FlaskReact Class

#### Methods

##### `__init__(app=None)`
Initialize the Flask-React extension.

##### `init_app(app)`
Initialize the extension with a Flask application.

##### `render_component(component_name, props=None, template_data=None)`
Render a React component to HTML string.

- `component_name`: Name of the component to render
- `props`: Props to pass to the component
- `template_data`: Additional template data for Jinja2 processing

##### `render_template(component_name, **context)`
Render a React component as a Flask template (similar to `render_template()`).

##### `list_components()`
List all available React components.

##### `clear_cache()`
Clear the component cache.

### NodeRenderer Class

#### Methods

##### `render_component(component_name, props=None)`
Render a React component to HTML string using Node.js subprocess.

##### `list_components()`
List all available components in the components directory.

##### `clear_cache()`
Clear the component cache.

##### `get_component_info(component_name)`
Get detailed information about a specific component including file path, size, and modification time.

### Template Globals

#### `react_component(component_name, **props)`
Render a React component within a Jinja2 template.

#### `to_react_props(value)`
Convert a Python value to React props format (JSON).

### Utility Functions

#### `react_response(component_name, props=None, status_code=200, headers=None)`
Create a Flask response with rendered React component.

## Error Handling

### Exceptions

- `FlaskReactError`: Base exception for Flask-React errors
- `ComponentNotFoundError`: Raised when a component cannot be found
- `RenderError`: Raised when component rendering fails
- `JavaScriptEngineError`: Raised when there's an issue with Node.js
- `ComponentCompileError`: Raised when component compilation fails

### Error Handling Example

```python
from flask_react.exceptions import ComponentNotFoundError, RenderError

@app.route('/render/<component_name>')
def render_component(component_name):
    try:
        return react.render_template(component_name, data=request.args)
    except ComponentNotFoundError:
        return "Component not found", 404
    except RenderError as e:
        app.logger.error(f"Render error: {e}")
        return "Rendering failed", 500
```

## Performance Considerations

### Component Caching

Components are cached by default to improve performance. This affects both Python-level caching and Node.js Babel compilation caching:

```python
# Disable caching in development (affects both Python and Node.js caching)
app.config['FLASK_REACT_CACHE_COMPONENTS'] = not app.debug

# Clear cache manually (Python-level cache only)
react.clear_cache()
```

When `FLASK_REACT_CACHE_COMPONENTS` is `False`:
- Python-level component cache is disabled
- Node.js require cache is cleared on each render for hot reloading
- Babel compilation cache is disabled

### Production Optimization

1. **Enable caching**: Keep `FLASK_REACT_CACHE_COMPONENTS = True` in production
2. **Optimize Node.js timeout**: Set appropriate `FLASK_REACT_NODE_TIMEOUT` based on component complexity
3. **Minimize component complexity**: Keep components simple for faster rendering
4. **Consider client-side hydration**: For interactive components
5. **Use Node.js process pools**: For high-traffic applications, consider implementing process pooling

## Development Tips

### Hot Reloading

In development mode, components are automatically reloaded when changed:

```python
app.config['FLASK_REACT_AUTO_RELOAD'] = True  # Default in debug mode
```

### Debugging

Enable detailed error messages:

```python
app.config['DEBUG'] = True
app.config['FLASK_REACT_DEBUG'] = True
```

### Component Organization

Organize components in subdirectories:

```
components/
├── layout/
│   ├── Header.jsx
│   ├── Footer.jsx
│   └── Navigation.jsx
├── forms/
│   ├── ContactForm.jsx
│   └── LoginForm.jsx
└── common/
    ├── Button.jsx
    └── Modal.jsx
```

Access with dot notation or subdirectory paths:

```python
# These are equivalent
react.render_template('layout.Header')
react.render_template('layout/Header')
```

## Best Practices

1. **Keep components pure**: Components should be pure functions without side effects
2. **Use props effectively**: Pass all necessary data as props
3. **Handle edge cases**: Always check for null/undefined props
4. **Style consistently**: Use consistent styling approaches
5. **Test components**: Write tests for your React components
6. **Error boundaries**: Implement error handling in components
7. **Performance**: Use React best practices for performance

## Limitations

1. **Server-side only**: Components are rendered server-side; no client-side interactivity
2. **Node.js dependency**: Requires Node.js to be installed and accessible
3. **No React hooks**: Server-side rendering doesn't support React hooks
4. **Limited React features**: Some React features may not work in server-side context
5. **Performance overhead**: Server-side rendering adds computational overhead
6. **Process overhead**: Each render creates a new Node.js subprocess

## Migration Guide

### From Jinja2 Templates

```python
# Before (Jinja2)
@app.route('/users')
def users():
    return render_template('users.html', users=get_users())

# After (Flask-React)
@app.route('/users')
def users():
    return react.render_template('UserList', users=get_users())
```

### Component Conversion

```html
<!-- Before: users.html (Jinja2) -->
<div>
    <h1>Users</h1>
    {% for user in users %}
        <div class="user">{{ user.name }}</div>
    {% endfor %}
</div>
```

```jsx
// After: UserList.jsx (React)
function UserList({ users }) {
    return (
        <div>
            <h1>Users</h1>
            {users.map(user => (
                <div key={user.id} className="user">{user.name}</div>
            ))}
        </div>
    );
}
```

## Contributing

Contributions are welcome! Please see the contributing guidelines in the repository.

## License

MIT License - see LICENSE file for details.
