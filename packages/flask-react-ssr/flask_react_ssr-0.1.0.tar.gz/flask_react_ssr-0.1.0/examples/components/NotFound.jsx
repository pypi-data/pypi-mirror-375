const React = require('react');

function NotFound({ message }) {
    return (
        <div className="not-found">
            <div className="not-found-content">
                <div className="error-code">404</div>
                <h1>Page Not Found</h1>
                <p>{message || "The page you're looking for doesn't exist."}</p>
                <div className="actions">
                    <a href="/" className="btn btn-primary">Go Home</a>
                    <button onClick={() => window.history.back()} className="btn btn-outline">
                        Go Back
                    </button>
                </div>
            </div>
            
            <style jsx>{`
                .not-found {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                
                .not-found-content {
                    text-align: center;
                    max-width: 500px;
                    padding: 2rem;
                }
                
                .error-code {
                    font-size: 8rem;
                    font-weight: bold;
                    opacity: 0.3;
                    margin-bottom: 1rem;
                }
                
                .not-found-content h1 {
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }
                
                .not-found-content p {
                    font-size: 1.1rem;
                    opacity: 0.9;
                    margin-bottom: 2rem;
                }
                
                .actions {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                
                .btn {
                    padding: 0.75rem 1.5rem;
                    border: 2px solid white;
                    border-radius: 6px;
                    text-decoration: none;
                    cursor: pointer;
                    font-size: 1rem;
                    font-weight: 500;
                    transition: all 0.3s;
                }
                
                .btn-primary {
                    background: white;
                    color: #667eea;
                }
                
                .btn-primary:hover {
                    background: #f8f9fa;
                    transform: translateY(-2px);
                }
                
                .btn-outline {
                    background: transparent;
                    color: white;
                }
                
                .btn-outline:hover {
                    background: white;
                    color: #667eea;
                    transform: translateY(-2px);
                }
            `}</style>
        </div>
    );
}
module.exports = NotFound;