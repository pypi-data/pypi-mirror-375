# Flask-React

A Flask extension for server-side React component rendering with template-like functionality using Node.js.

## Features

- 🚀 Server-side React component rendering with Node.js
- 🎯 Flask template integration (like Jinja2)
- 🔄 Support for conditions, loops, and data binding
- 📦 Component management system
- 🎨 Props passing and state management
- 🔧 Easy Flask integration
- ⚡ Fast Node.js-based rendering engine

## Prerequisites

**Node.js is required** for server-side React rendering. Install Node.js before using this extension:

```bash
# Install Node.js (https://nodejs.org/)
# Verify installation:
node --version
npm --version
```

## Installation

```bash
pip install flask-react-ssr
```

## Quick Start

```python
from flask import Flask
from flask_react import FlaskReact

app = Flask(__name__)
react = FlaskReact(app)

@app.route('/')
def home():
    return react.render_component('HelloWorld', {
        'name': 'Flask React',
        'items': ['Feature 1', 'Feature 2', 'Feature 3']
    })
```

## Usage

### Creating Components

Create React components in your `components/` directory:

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

### Template-like Rendering

```python
@app.route('/user/<username>')
def user_profile(username):
    user_data = get_user(username)
    return react.render_component('UserProfile', {
        'user': user_data,
        'is_authenticated': current_user.is_authenticated,
        'permissions': get_user_permissions(username)
    })
```

### Conditional Rendering

```jsx
// components/UserProfile.jsx
function UserProfile({ user, is_authenticated, permissions }) {
    return (
        <div>
            <h1>{user.name}</h1>
            {is_authenticated && (
                <div className="authenticated-content">
                    <p>Welcome back!</p>
                    {permissions.includes('admin') && (
                        <button>Admin Panel</button>
                    )}
                </div>
            )}
            {!is_authenticated && (
                <div>
                    <p>Please log in to see more content.</p>
                </div>
            )}
        </div>
    );
}
```

## Configuration

```python
# Basic configuration
app.config['FLASK_REACT_COMPONENTS_DIR'] = 'components'  # Components directory
app.config['FLASK_REACT_CACHE_COMPONENTS'] = True        # Enable caching
app.config['FLASK_REACT_NODE_EXECUTABLE'] = 'node'       # Node.js executable path
app.config['FLASK_REACT_NODE_TIMEOUT'] = 30              # Node.js process timeout
```

## Setup for Development

1. **Install Node.js dependencies**:
```bash
# Flask-React includes a package.json with all required dependencies
npm install
```

2. **Create components directory**:
```bash
mkdir components
```

The `package.json` includes all necessary dependencies:
- React and ReactDOM for SSR
- Babel presets for JSX, TypeScript, and modern JavaScript
- Proper Node.js version requirements (16+)

## Troubleshooting

### Node.js Not Found
If you get "Node.js not found" errors:
- Ensure Node.js is installed and in your PATH
- Set the Node.js path explicitly: `app.config['FLASK_REACT_NODE_EXECUTABLE'] = '/path/to/node'`

### Component Not Found
- Check that your components are in the correct directory
- Verify file extensions (.jsx, .js, .ts, .tsx are supported)
- Ensure component names match file names

### Rendering Timeout
- Increase timeout: `app.config['FLASK_REACT_NODE_TIMEOUT'] = 60`
- Check for infinite loops in your components

## License

MIT License
