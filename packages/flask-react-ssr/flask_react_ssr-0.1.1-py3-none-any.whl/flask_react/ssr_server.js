
const React = require('react');
const { renderToString } = require('react-dom/server');

// Get cache setting from command line arguments or default to true
const cacheEnabled = process.argv[4] === 'true' || process.argv[4] === undefined;

// Setup Babel for JSX transformation
try {
    require('@babel/register')({
        presets: ['@babel/preset-react'],
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
        cache: cacheEnabled // cache configuration
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
