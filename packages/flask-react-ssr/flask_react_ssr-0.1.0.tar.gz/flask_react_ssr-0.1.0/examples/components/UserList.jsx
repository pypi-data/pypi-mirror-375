const React = require('react');

function UserList(props) {
    var users = props.users;
    var current_user = props.current_user;
    var can_edit = props.can_edit;
    var page_title = props.page_title;
    
    // Create user cards
    var userCards = [];
    if (users && users.length > 0) {
        for (var i = 0; i < users.length; i++) {
            var user = users[i];
            
            // User actions
            var userActions = [
                React.createElement('a', {
                    href: '/user/' + user.id,
                    className: 'btn btn-outline',
                    style: {
                        padding: '0.375rem 0.75rem',
                        border: '1px solid #6c757d',
                        borderRadius: '4px',
                        backgroundColor: 'transparent',
                        color: '#6c757d',
                        textDecoration: 'none',
                        fontSize: '0.875rem',
                        marginRight: '0.5rem'
                    }
                }, 'View Profile')
            ];
            
            if (can_edit) {
                userActions.push(React.createElement('button', {
                    className: 'btn btn-outline',
                    style: {
                        padding: '0.375rem 0.75rem',
                        border: '1px solid #6c757d',
                        borderRadius: '4px',
                        backgroundColor: 'transparent',
                        color: '#6c757d',
                        fontSize: '0.875rem',
                        marginRight: '0.5rem'
                    }
                }, 'Edit'));
                
                if (current_user && current_user.id !== user.id) {
                    userActions.push(React.createElement('button', {
                        className: 'btn btn-danger',
                        style: {
                            padding: '0.375rem 0.75rem',
                            border: 'none',
                            borderRadius: '4px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            fontSize: '0.875rem'
                        }
                    }, 'Delete'));
                }
            }
            
            userCards.push(React.createElement('div', {
                key: user.id,
                className: 'user-card',
                style: {
                    background: 'white',
                    border: '1px solid #e9ecef',
                    borderRadius: '8px',
                    padding: '1.5rem',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }
            }, [
                React.createElement('div', {
                    className: 'user-info'
                }, [
                    React.createElement('h3', {
                        style: {
                            margin: '0 0 0.5rem 0',
                            color: '#2c3e50'
                        }
                    }, user.name),
                    React.createElement('p', {
                        className: 'email',
                        style: {
                            color: '#6c757d',
                            marginBottom: '1rem'
                        }
                    }, user.email),
                    React.createElement('span', {
                        className: 'role role-' + user.role,
                        style: {
                            display: 'inline-block',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            textTransform: 'uppercase',
                            backgroundColor: user.role === 'admin' ? '#dc3545' : '#28a745',
                            color: 'white'
                        }
                    }, user.role)
                ]),
                React.createElement('div', {
                    className: 'user-actions',
                    style: {
                        marginTop: '1rem',
                        display: 'flex',
                        gap: '0.5rem',
                        flexWrap: 'wrap'
                    }
                }, userActions)
            ]));
        }
    }
    
    return React.createElement('div', {
        className: 'user-list',
        style: {
            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '2rem'
        }
    }, [
        // Header
        React.createElement('header', {
            style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem'
            }
        }, [
            React.createElement('h1', null, page_title || 'Users'),
            can_edit ? React.createElement('button', {
                className: 'btn btn-primary',
                style: {
                    padding: '0.5rem 1rem',
                    border: 'none',
                    borderRadius: '4px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                }
            }, 'Add New User') : null
        ]),
        
        // User stats
        React.createElement('div', {
            className: 'user-stats',
            style: {
                background: '#f8f9fa',
                padding: '1rem',
                borderRadius: '8px',
                marginBottom: '2rem'
            }
        }, [
            React.createElement('p', null, [
                'Total users: ',
                React.createElement('strong', null, users ? users.length : 0)
            ]),
            current_user ? React.createElement('p', null, [
                'Logged in as: ',
                React.createElement('strong', null, current_user.name),
                ' (' + current_user.role + ')'
            ]) : null
        ]),
        
        // User grid or empty state
        users && users.length > 0 ? 
            React.createElement('div', {
                className: 'user-grid',
                style: {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '1.5rem'
                }
            }, userCards) :
            React.createElement('div', {
                className: 'empty-state',
                style: {
                    textAlign: 'center',
                    padding: '3rem',
                    color: '#6c757d'
                }
            }, React.createElement('p', null, 'No users found.'))
    ]);
}

module.exports = UserList;
