"""
CLI tool for Flask-React extension.
Provides commands to manage React components.
"""

import argparse
import os
import sys
from pathlib import Path


def create_component(name, components_dir="components", template="basic"):
    """Create a new React component."""
    components_path = Path(components_dir)
    components_path.mkdir(exist_ok=True)

    component_file = components_path / f"{name}.jsx"

    if component_file.exists():
        print(f"Component '{name}' already exists!")
        return False

    templates = {
        "basic": f"""function {name}({{ children }}) {{
    return (
        <div className="{name.lower()}">
            {{children}}
        </div>
    );
}}""",
        "page": f"""function {name}({{ title, content }}) {{
    return (
        <div className="page">
            <header>
                <h1>{{title || '{name}'}}</h1>
            </header>
            <main>
                {{content && (
                    <div className="content">
                        {{content}}
                    </div>
                )}}
            </main>
        </div>
    );
}}""",
        "list": f"""function {name}({{ items, title }}) {{
    return (
        <div className="{name.lower()}">
            {{title && <h2>{{title}}</h2>}}
            {{items && items.length > 0 ? (
                <ul className="items-list">
                    {{items.map((item, index) => (
                        <li key={{index}} className="item">
                            {{typeof item === 'object' ? item.name || item.title : item}}
                        </li>
                    ))}}
                </ul>
            ) : (
                <p className="empty-message">No items to display</p>
            )}}
        </div>
    );
}}""",
        "form": f"""function {name}({{ fields, action, method, title }}) {{
    return (
        <div className="form-container">
            {{title && <h2>{{title}}</h2>}}
            <form action={{action || '#'}} method={{method || 'POST'}} className="form">
                {{fields && fields.map((field, index) => (
                    <div key={{index}} className="form-group">
                        <label htmlFor={{field.name}} className="form-label">
                            {{field.label}}
                            {{field.required && <span className="required">*</span>}}
                        </label>
                        {{field.type === 'textarea' ? (
                            <textarea
                                id={{field.name}}
                                name={{field.name}}
                                className="form-control"
                                required={{field.required}}
                                placeholder={{field.placeholder}}
                                rows={{field.rows || 4}}
                            />
                        ) : (
                            <input
                                type={{field.type || 'text'}}
                                id={{field.name}}
                                name={{field.name}}
                                className="form-control"
                                required={{field.required}}
                                placeholder={{field.placeholder}}
                            />
                        )}}
                    </div>
                ))}}
                <div className="form-actions">
                    <button type="submit" className="btn btn-primary">Submit</button>
                </div>
            </form>
        </div>
    );
}}""",
    }

    component_code = templates.get(template, templates["basic"])

    with open(component_file, "w", encoding="utf-8") as f:
        f.write(component_code)

    print(f"Component '{name}' created successfully at {component_file}")
    return True


def list_components(components_dir="components"):
    """List all available components."""
    components_path = Path(components_dir)

    if not components_path.exists():
        print(f"Components directory '{components_dir}' does not exist.")
        return

    components = []
    for ext in ["*.jsx", "*.js"]:
        components.extend(components_path.glob(ext))

    if not components:
        print("No components found.")
        return

    print(f"Components in '{components_dir}':")
    for component in sorted(components):
        print(f"  - {component.stem}")


def remove_component(name, components_dir="components"):
    """Remove a React component."""
    components_path = Path(components_dir)

    for ext in [".jsx", ".js"]:
        component_file = components_path / f"{name}{ext}"
        if component_file.exists():
            component_file.unlink()
            print(f"Component '{name}' removed successfully.")
            return True

    print(f"Component '{name}' not found.")
    return False


def init_project(project_dir="."):
    """Initialize a new Flask-React project."""
    project_path = Path(project_dir)

    # Create directories
    directories = ["components", "templates", "static/css", "static/js"]

    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    # Create basic app.py
    app_content = '''"""
Flask-React application.
"""

from flask import Flask
from flask_react import FlaskReact

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize Flask-React
react = FlaskReact(app)


@app.route('/')
def home():
    """Homepage."""
    return react.render_template('HomePage',
        title='Welcome to Flask-React',
        message='Your Flask-React application is ready!'
    )


if __name__ == '__main__':
    app.run(debug=True)
'''

    app_file = project_path / "app.py"
    if not app_file.exists():
        with open(app_file, "w", encoding="utf-8") as f:
            f.write(app_content)
        print("Created app.py")

    # Create basic HomePage component
    homepage_content = """function HomePage({ title, message }) {
    return (
        <div className="homepage">
            <header>
                <h1>{title || 'Flask-React App'}</h1>
            </header>
            <main>
                <p>{message || 'Welcome to your new Flask-React application!'}</p>
                <div className="getting-started">
                    <h2>Getting Started</h2>
                    <ul>
                        <li>Edit this component in <code>components/HomePage.jsx</code></li>
                        <li>Add new routes in <code>app.py</code></li>
                        <li>Create new components with <code>flask-react create ComponentName</code></li>
                    </ul>
                </div>
            </main>
        </div>
    );
}"""

    homepage_file = project_path / "components" / "HomePage.jsx"
    if not homepage_file.exists():
        with open(homepage_file, "w", encoding="utf-8") as f:
            f.write(homepage_content)
        print("Created components/HomePage.jsx")

    # Create requirements.txt
    requirements_content = """Flask>=2.0.0
flask-react>=0.1.0
PyExecJS>=1.5.1
"""

    requirements_file = project_path / "requirements.txt"
    if not requirements_file.exists():
        with open(requirements_file, "w", encoding="utf-8") as f:
            f.write(requirements_content)
        print("Created requirements.txt")

    print(f"Flask-React project initialized in '{project_dir}'")
    print("Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run the application: python app.py")
    print("  3. Open http://localhost:5000 in your browser")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Flask-React CLI tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create component command
    create_parser = subparsers.add_parser("create", help="Create a new React component")
    create_parser.add_argument("name", help="Component name")
    create_parser.add_argument(
        "--dir", default="components", help="Components directory"
    )
    create_parser.add_argument(
        "--template",
        choices=["basic", "page", "list", "form"],
        default="basic",
        help="Component template",
    )

    # List components command
    list_parser = subparsers.add_parser("list", help="List all components")
    list_parser.add_argument("--dir", default="components", help="Components directory")

    # Remove component command
    remove_parser = subparsers.add_parser("remove", help="Remove a component")
    remove_parser.add_argument("name", help="Component name")
    remove_parser.add_argument(
        "--dir", default="components", help="Components directory"
    )

    # Initialize project command
    init_parser = subparsers.add_parser(
        "init", help="Initialize a new Flask-React project"
    )
    init_parser.add_argument("--dir", default=".", help="Project directory")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "create":
        create_component(args.name, args.dir, args.template)
    elif args.command == "list":
        list_components(args.dir)
    elif args.command == "remove":
        remove_component(args.name, args.dir)
    elif args.command == "init":
        init_project(args.dir)


if __name__ == "__main__":
    main()
