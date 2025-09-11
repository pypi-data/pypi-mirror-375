const React = require('react');

function Dashboard({ current_user, stats, recent_users, recent_products, is_admin }) {
    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <h1>Dashboard</h1>
                {current_user && (
                    <div className="user-info">
                        Welcome back, <strong>{current_user.name}</strong>!
                    </div>
                )}
            </header>
            
            {/* Stats Overview */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-number">{stats.total_users}</div>
                    <div className="stat-label">Total Users</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">{stats.total_products}</div>
                    <div className="stat-label">Products</div>
                </div>
                {is_admin && (
                    <div className="stat-card">
                        <div className="stat-number">{stats.admin_users}</div>
                        <div className="stat-label">Admin Users</div>
                    </div>
                )}
                <div className="stat-card">
                    <div className="stat-number">{stats.categories}</div>
                    <div className="stat-label">Categories</div>
                </div>
            </div>
            
            <div className="dashboard-content">
                {/* Recent Users */}
                <section className="dashboard-section">
                    <h2>Recent Users</h2>
                    {recent_users && recent_users.length > 0 ? (
                        <div className="recent-items">
                            {recent_users.map((user) => (
                                <div key={user.id} className="recent-item">
                                    <div className="item-avatar">
                                        {user.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="item-details">
                                        <div className="item-name">{user.name}</div>
                                        <div className="item-meta">{user.email}</div>
                                        <span className={`role role-${user.role}`}>
                                            {user.role}
                                        </span>
                                    </div>
                                    <div className="item-actions">
                                        <a href={`/user/${user.id}`} className="btn btn-sm">View</a>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="empty-message">No recent users</p>
                    )}
                    <div className="section-footer">
                        <a href="/users" className="link">View all users →</a>
                    </div>
                </section>
                
                {/* Recent Products */}
                <section className="dashboard-section">
                    <h2>Recent Products</h2>
                    {recent_products && recent_products.length > 0 ? (
                        <div className="recent-items">
                            {recent_products.map((product) => (
                                <div key={product.id} className="recent-item">
                                    <div className="item-icon">📦</div>
                                    <div className="item-details">
                                        <div className="item-name">{product.name}</div>
                                        <div className="item-meta">
                                            ${product.price} • {product.category}
                                        </div>
                                    </div>
                                    <div className="item-actions">
                                        <button className="btn btn-sm">Edit</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="empty-message">No recent products</p>
                    )}
                    <div className="section-footer">
                        <a href="/products" className="link">View all products →</a>
                    </div>
                </section>
            </div>
            
            {/* Admin Only Section */}
            {is_admin && (
                <section className="dashboard-section admin-section">
                    <h2>🔧 Admin Tools</h2>
                    <div className="admin-tools">
                        <button className="tool-btn">
                            <span className="tool-icon">👥</span>
                            <span>Manage Users</span>
                        </button>
                        <button className="tool-btn">
                            <span className="tool-icon">📊</span>
                            <span>Analytics</span>
                        </button>
                        <button className="tool-btn">
                            <span className="tool-icon">⚙️</span>
                            <span>Settings</span>
                        </button>
                        <button className="tool-btn">
                            <span className="tool-icon">🗄️</span>
                            <span>Database</span>
                        </button>
                    </div>
                </section>
            )}
            
            <style jsx>{`
                .dashboard {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #f8f9fa;
                    min-height: 100vh;
                }
                
                .dashboard-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                }
                
                .dashboard-header h1 {
                    color: #2c3e50;
                    margin: 0;
                }
                
                .user-info {
                    color: #6c757d;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 3rem;
                }
                
                .stat-card {
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                
                .stat-number {
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 0.5rem;
                }
                
                .stat-label {
                    color: #6c757d;
                    font-weight: 500;
                }
                
                .dashboard-content {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 2rem;
                    margin-bottom: 2rem;
                }
                
                .dashboard-section {
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .dashboard-section h2 {
                    margin: 0 0 1.5rem 0;
                    color: #2c3e50;
                    font-size: 1.25rem;
                }
                
                .recent-items {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .recent-item {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 1rem;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
                
                .item-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #007bff;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                }
                
                .item-icon {
                    font-size: 1.5rem;
                }
                
                .item-details {
                    flex: 1;
                }
                
                .item-name {
                    font-weight: 600;
                    color: #2c3e50;
                    margin-bottom: 0.25rem;
                }
                
                .item-meta {
                    color: #6c757d;
                    font-size: 0.875rem;
                }
                
                .role {
                    display: inline-block;
                    padding: 0.125rem 0.375rem;
                    border-radius: 3px;
                    font-size: 0.75rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    margin-top: 0.25rem;
                }
                
                .role-admin {
                    background: #dc3545;
                    color: white;
                }
                
                .role-user {
                    background: #28a745;
                    color: white;
                }
                
                .btn {
                    padding: 0.375rem 0.75rem;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    background: white;
                    color: #495057;
                    text-decoration: none;
                    cursor: pointer;
                    font-size: 0.875rem;
                }
                
                .btn-sm {
                    padding: 0.25rem 0.5rem;
                    font-size: 0.75rem;
                }
                
                .section-footer {
                    margin-top: 1.5rem;
                    padding-top: 1rem;
                    border-top: 1px solid #dee2e6;
                }
                
                .link {
                    color: #007bff;
                    text-decoration: none;
                    font-weight: 500;
                }
                
                .empty-message {
                    color: #6c757d;
                    font-style: italic;
                    text-align: center;
                    padding: 2rem 0;
                }
                
                .admin-section {
                    grid-column: 1 / -1;
                    border: 2px solid #ffc107;
                    background: linear-gradient(135deg, #fff3cd 0%, #ffffff 100%);
                }
                
                .admin-tools {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 1rem;
                }
                
                .tool-btn {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 1.5rem;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                
                .tool-btn:hover {
                    background: #f8f9fa;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                
                .tool-icon {
                    font-size: 1.5rem;
                }
                
                @media (max-width: 768px) {
                    .dashboard-content {
                        grid-template-columns: 1fr;
                    }
                    
                    .stats-grid {
                        grid-template-columns: repeat(2, 1fr);
                    }
                }
            `}</style>
        </div>
    );
}
module.exports = Dashboard;
