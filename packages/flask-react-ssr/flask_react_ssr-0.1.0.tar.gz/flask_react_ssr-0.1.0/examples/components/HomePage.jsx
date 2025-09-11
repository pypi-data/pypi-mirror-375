const React = require('react');

function HomePage(props) {
    var title = props.title;
    var subtitle = props.subtitle;
    var features = props.features;
    
    // Create feature list items
    var featureItems = [];
    if (features && features.length > 0) {
        for (var i = 0; i < features.length; i++) {
            featureItems.push(
                React.createElement('li', {
                    key: i,
                    className: 'feature-item',
                    style: {
                        padding: '0.5rem 0',
                        color: '#27ae60',
                        fontWeight: '500'
                    }
                }, '✓ ' + features[i])
            );
        }
    }
    
    return React.createElement('div', {
        className: 'homepage',
        style: {
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            maxWidth: '800px',
            margin: '0 auto',
            padding: '2rem'
        }
    }, [
        // Header section
        React.createElement('header', {
            className: 'hero',
            style: {
                textAlign: 'center',
                marginBottom: '3rem'
            }
        }, [
            React.createElement('h1', {
                style: {
                    color: '#2c3e50',
                    fontSize: '2.5rem',
                    marginBottom: '1rem'
                }
            }, title || 'Welcome to Flask-React'),
            React.createElement('p', {
                className: 'subtitle',
                style: {
                    color: '#7f8c8d',
                    fontSize: '1.2rem'
                }
            }, subtitle || 'Server-side React rendering with Flask')
        ]),
        
        // Main content
        React.createElement('main', {
            className: 'main-content'
        }, [
            // Features section
            React.createElement('section', {
                className: 'features',
                style: { marginBottom: '2rem' }
            }, [
                React.createElement('h2', null, 'Features'),
                features && features.length > 0 ? 
                    React.createElement('ul', {
                        className: 'feature-list',
                        style: {
                            listStyle: 'none',
                            padding: '0'
                        }
                    }, featureItems) : null
            ]),
            
            // Getting started section
            React.createElement('section', {
                className: 'getting-started'
            }, [
                React.createElement('h2', null, 'Getting Started'),
                React.createElement('p', null, 'This is a React component rendered server-side by Flask!'),
                React.createElement('div', {
                    className: 'code-example',
                    style: {
                        background: '#f8f9fa',
                        borderRadius: '8px',
                        padding: '1rem',
                        overflowX: 'auto'
                    }
                }, React.createElement('pre', {
                    style: { margin: '0' }
                }, React.createElement('code', {
                    style: {
                        fontFamily: '"Monaco", "Menlo", monospace',
                        fontSize: '0.9rem'
                    }
                }, "@app.route('/')\ndef home():\n    return react.render_template('HomePage', \n        title='Welcome to Flask-React',\n        features=['Feature 1', 'Feature 2']\n    )")))
            ])
        ])
    ]);
}

module.exports = HomePage;
