# Flask-React Demo Application

This example demonstrates all the key features of the Flask-React extension.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

## Features Demonstrated

- **Server-side React rendering**: All components are rendered server-side
- **Template-like conditions**: Components use conditional rendering based on props
- **Data binding**: Flask data is passed as props to React components
- **Component reusability**: Same components used across different pages
- **List rendering**: Dynamic list rendering with filtering
- **Form handling**: Form components with validation
- **User authentication simulation**: Role-based rendering
- **Error handling**: 404 pages and error components
- **Styling**: Inline styles and CSS classes

## Routes

- `/` - Homepage with features overview
- `/users` - User list with admin controls
- `/user/<id>` - User profile with conditional content
- `/products` - Product list with filtering
- `/dashboard` - Admin dashboard with multiple components
- `/form-example` - Contact form example
- `/api/components` - API to list available components

## Components

- `HomePage.jsx` - Landing page with feature showcase
- `UserList.jsx` - User listing with role-based controls
- `UserProfile.jsx` - User profile with conditional sections
- `Dashboard.jsx` - Admin dashboard with statistics
- `ProductList.jsx` - Product catalog with filtering
- `ContactForm.jsx` - Form component with validation
- `NotFound.jsx` - 404 error page

Each component demonstrates different Flask-React features and React patterns that work with server-side rendering.
