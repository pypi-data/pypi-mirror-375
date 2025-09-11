"""
Example Flask application demonstrating Flask-React usage.
"""

from flask import Flask, request, jsonify
from flask_react import FlaskReact

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['FLASK_REACT_COMPONENTS_DIR'] = 'components'

# Initialize Flask-React
react = FlaskReact(app)

# Sample data
users = [
    {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'role': 'admin'},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'user'},
    {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'role': 'user'},
]

products = [
    {'id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics'},
    {'id': 2, 'name': 'Chair', 'price': 149.99, 'category': 'Furniture'},
    {'id': 3, 'name': 'Book', 'price': 19.99, 'category': 'Education'},
]


@app.route('/')
def home():
    """Homepage with welcome component."""
    return react.render_template('HomePage', 
        title='Welcome to Flask-React',
        subtitle='Server-side React rendering with Flask',
        features=[
            'Server-side rendering',
            'Template-like conditions',
            'Props passing',
            'Component reusability'
        ]
    )


@app.route('/users')
def user_list():
    """User list page demonstrating conditional rendering."""
    current_user = {'id': 1, 'role': 'admin'}  # Mock current user
    
    return react.render_template('UserList',
        users=users,
        current_user=current_user,
        can_edit=current_user['role'] == 'admin',
        page_title='User Management'
    )

@app.route('/user/<int:user_id>')
def user_detail(user_id):
    """User detail page with conditional content."""
    user = next((u for u in users if u['id'] == user_id), None)
    current_user = {'id': 1, 'role': 'admin'}  # Mock current user
    
    if not user:
        return react.render_template('NotFound', 
            message=f'User with ID {user_id} not found'
        ), 404
    
    return react.render_template('UserProfile',
        user=user,
        current_user=current_user,
        is_own_profile=current_user['id'] == user['id'],
        can_edit=current_user['role'] == 'admin' or current_user['id'] == user['id']
    )


@app.route('/products')
def product_list():
    """Product list with filtering and search."""
    category = request.args.get('category')
    search = request.args.get('search', '')
    
    filtered_products = products
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'].lower() == category.lower()]
    
    if search:
        filtered_products = [p for p in filtered_products 
                           if search.lower() in p['name'].lower()]
    
    categories = list(set(p['category'] for p in products))
    
    return react.render_template('ProductList',
        products=filtered_products,
        categories=categories,
        current_category=category,
        search_query=search,
        total_products=len(products),
        filtered_count=len(filtered_products)
    )


@app.route('/dashboard')
def dashboard():
    """Dashboard with multiple components and conditions."""
    current_user = {'id': 1, 'name': 'John Doe', 'role': 'admin'}
    
    stats = {
        'total_users': len(users),
        'total_products': len(products),
        'admin_users': len([u for u in users if u['role'] == 'admin']),
        'categories': len(set(p['category'] for p in products))
    }
    
    recent_users = users[-3:]  # Last 3 users
    recent_products = products[-3:]  # Last 3 products
    
    return react.render_template('Dashboard',
        current_user=current_user,
        stats=stats,
        recent_users=recent_users,
        recent_products=recent_products,
        is_admin=current_user['role'] == 'admin'
    )


@app.route('/form-example')
def form_example():
    """Example form component."""
    return react.render_template('ContactForm',
        title='Contact Us',
        fields=[
            {'name': 'name', 'type': 'text', 'label': 'Name', 'required': True},
            {'name': 'email', 'type': 'email', 'label': 'Email', 'required': True},
            {'name': 'message', 'type': 'textarea', 'label': 'Message', 'required': True}
        ]
    )


@app.route('/api/components')
def list_components():
    """API endpoint to list available components."""
    components = react.list_components()
    return jsonify({'components': components})


@app.route('/clear-cache')
def clear_cache():
    """Clear component cache (useful in development)."""
    react.clear_cache()
    return jsonify({'message': 'Component cache cleared'})


if __name__ == '__main__':
    app.run(debug=True)
