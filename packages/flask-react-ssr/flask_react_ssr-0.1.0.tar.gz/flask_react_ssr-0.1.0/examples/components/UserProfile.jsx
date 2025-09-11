const React = require('react');

function UserProfile({ user, current_user, is_own_profile, can_edit }) {
    props = {
        'title': '{{ user.name }}\'s Profile',
        'message': '{{ "Hello " + user.name if user else "Please login" }}',
        'items': '{{ user.items | tojson }}'
    }
    if (!user) {
        return (
            <div className="user-profile">
                <div className="error">
                    <h1>User Not Found</h1>
                    <p>The requested user could not be found.</p>
                    <a href="/users" className="btn btn-primary">Back to Users</a>
                </div>
            </div>
        );
    }
    
    return (
        <div className="user-profile">
            <nav className="breadcrumb">
                <a href="/">Home</a> / <a href="/users">Users</a> / {user.name}
            </nav>
            
            <div className="profile-header">
                <div className="avatar">
                    {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="user-details">
                    <h1>{user.name}</h1>
                    <p className="email">{user.email}</p>
                    <span className={`role role-${user.role}`}>
                        {user.role}
                    </span>
                    
                    {is_own_profile && (
                        <p className="own-profile-note">This is your profile</p>
                    )}
                </div>
                
                <div className="profile-actions">
                    {can_edit && (
                        <button className="btn btn-primary">
                            {is_own_profile ? 'Edit Profile' : 'Edit User'}
                        </button>
                    )}
                    {!is_own_profile && current_user && current_user.role === 'admin' && (
                        <button className="btn btn-outline">Send Message</button>
                    )}
                </div>
            </div>
            
            <div className="profile-content">
                <div className="info-sections">
                    <section className="info-section">
                        <h2>Account Information</h2>
                        <div className="info-grid">
                            <div className="info-item">
                                <label>User ID</label>
                                <span>{user.id}</span>
                            </div>
                            <div className="info-item">
                                <label>Role</label>
                                <span className={`role role-${user.role}`}>
                                    {user.role}
                                </span>
                            </div>
                            <div className="info-item">
                                <label>Email</label>
                                <span>{user.email}</span>
                            </div>
                        </div>
                    </section>
                    
                    {current_user && current_user.role === 'admin' && (
                        <section className="info-section">
                            <h2>Admin Information</h2>
                            <div className="admin-notes">
                                <p>Additional admin-only information would appear here.</p>
                                {user.role === 'admin' ? (
                                    <div className="warning">
                                        <strong>Warning:</strong> This user has admin privileges.
                                    </div>
                                ) : (
                                    <div className="info">
                                        <strong>Note:</strong> This is a regular user account.
                                    </div>
                                )}
                            </div>
                        </section>
                    )}
                </div>
                
                <aside className="sidebar">
                    <div className="quick-actions">
                        <h3>Quick Actions</h3>
                        <ul>
                            {can_edit && (
                                <li><a href="#" className="action-link">Change Password</a></li>
                            )}
                            {is_own_profile && (
                                <li><a href="#" className="action-link">Update Preferences</a></li>
                            )}
                            {current_user && current_user.role === 'admin' && !is_own_profile && (
                                <>
                                    <li><a href="#" className="action-link">Reset Password</a></li>
                                    <li><a href="#" className="action-link">View Activity Log</a></li>
                                </>
                            )}
                        </ul>
                    </div>
                </aside>
            </div>
            
            <style jsx>{`
                .user-profile {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                
                .breadcrumb {
                    margin-bottom: 2rem;
                    color: #6c757d;
                }
                
                .breadcrumb a {
                    color: #007bff;
                    text-decoration: none;
                }
                
                .profile-header {
                    display: flex;
                    align-items: center;
                    gap: 2rem;
                    margin-bottom: 3rem;
                    padding: 2rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .avatar {
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    background: #007bff;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2rem;
                    font-weight: bold;
                }
                
                .user-details {
                    flex: 1;
                }
                
                .user-details h1 {
                    margin: 0 0 0.5rem 0;
                    color: #2c3e50;
                }
                
                .email {
                    color: #6c757d;
                    margin-bottom: 1rem;
                }
                
                .own-profile-note {
                    color: #28a745;
                    font-style: italic;
                    margin-top: 0.5rem;
                }
                
                .role {
                    display: inline-block;
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    font-size: 0.875rem;
                    font-weight: 500;
                    text-transform: uppercase;
                }
                
                .role-admin {
                    background: #dc3545;
                    color: white;
                }
                
                .role-user {
                    background: #28a745;
                    color: white;
                }
                
                .profile-actions {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                
                .profile-content {
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 2rem;
                }
                
                .info-section {
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                }
                
                .info-section h2 {
                    margin: 0 0 1.5rem 0;
                    color: #2c3e50;
                }
                
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }
                
                .info-item {
                    display: flex;
                    flex-direction: column;
                    gap: 0.25rem;
                }
                
                .info-item label {
                    font-weight: 600;
                    color: #495057;
                    font-size: 0.875rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .warning {
                    padding: 1rem;
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 4px;
                    color: #856404;
                }
                
                .info {
                    padding: 1rem;
                    background: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 4px;
                    color: #0c5460;
                }
                
                .sidebar {
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    height: fit-content;
                }
                
                .quick-actions h3 {
                    margin: 0 0 1rem 0;
                    color: #2c3e50;
                }
                
                .quick-actions ul {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                
                .quick-actions li {
                    margin-bottom: 0.5rem;
                }
                
                .action-link {
                    color: #007bff;
                    text-decoration: none;
                    font-weight: 500;
                }
                
                .action-link:hover {
                    text-decoration: underline;
                }
                
                .btn {
                    padding: 0.5rem 1rem;
                    border: none;
                    border-radius: 4px;
                    text-decoration: none;
                    cursor: pointer;
                    font-size: 0.875rem;
                    font-weight: 500;
                    display: inline-block;
                    text-align: center;
                }
                
                .btn-primary {
                    background: #007bff;
                    color: white;
                }
                
                .btn-outline {
                    background: transparent;
                    border: 1px solid #6c757d;
                    color: #6c757d;
                }
                
                .error {
                    text-align: center;
                    padding: 3rem;
                }
                
                @media (max-width: 768px) {
                    .profile-header {
                        flex-direction: column;
                        text-align: center;
                    }
                    
                    .profile-content {
                        grid-template-columns: 1fr;
                    }
                }
            `}</style>
        </div>
    );
}

module.exports = UserProfile;
