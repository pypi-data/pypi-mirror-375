const React = require('react');

function ContactForm({ title, fields }) {
    return (
        <div className="contact-form">
            <div className="form-container">
                <header className="form-header">
                    <h1>{title || 'Contact Form'}</h1>
                    <p>Please fill out the form below and we'll get back to you soon.</p>
                </header>
                
                <form className="form" method="POST" action="/contact">
                    {fields && fields.map((field, index) => (
                        <div key={index} className="form-group">
                            <label htmlFor={field.name} className="form-label">
                                {field.label}
                                {field.required && <span className="required">*</span>}
                            </label>
                            
                            {field.type === 'textarea' ? (
                                <textarea
                                    id={field.name}
                                    name={field.name}
                                    className="form-control"
                                    required={field.required}
                                    rows="4"
                                    placeholder={`Enter your ${field.label.toLowerCase()}`}
                                />
                            ) : (
                                <input
                                    type={field.type || 'text'}
                                    id={field.name}
                                    name={field.name}
                                    className="form-control"
                                    required={field.required}
                                    placeholder={`Enter your ${field.label.toLowerCase()}`}
                                />
                            )}
                        </div>
                    ))}
                    
                    <div className="form-group">
                        <label className="checkbox-label">
                            <input type="checkbox" name="newsletter" />
                            <span className="checkmark"></span>
                            Subscribe to our newsletter for updates
                        </label>
                    </div>
                    
                    <div className="form-actions">
                        <button type="submit" className="btn btn-primary">Send Message</button>
                        <button type="reset" className="btn btn-outline">Clear Form</button>
                    </div>
                </form>
                
                <div className="contact-info">
                    <h3>Other ways to reach us</h3>
                    <div className="contact-methods">
                        <div className="contact-method">
                            <span className="contact-icon">📧</span>
                            <div>
                                <strong>Email</strong>
                                <p>hello@example.com</p>
                            </div>
                        </div>
                        <div className="contact-method">
                            <span className="contact-icon">📞</span>
                            <div>
                                <strong>Phone</strong>
                                <p>+1 (555) 123-4567</p>
                            </div>
                        </div>
                        <div className="contact-method">
                            <span className="contact-icon">📍</span>
                            <div>
                                <strong>Address</strong>
                                <p>123 Main St, City, State 12345</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <style jsx>{`
                .contact-form {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .form-container {
                    background: white;
                    border-radius: 12px;
                    padding: 3rem;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    max-width: 600px;
                    width: 100%;
                }
                
                .form-header {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                
                .form-header h1 {
                    color: #2c3e50;
                    margin-bottom: 0.5rem;
                }
                
                .form-header p {
                    color: #6c757d;
                }
                
                .form-group {
                    margin-bottom: 1.5rem;
                }
                
                .form-label {
                    display: block;
                    margin-bottom: 0.5rem;
                    color: #495057;
                    font-weight: 600;
                }
                
                .required {
                    color: #dc3545;
                    margin-left: 0.25rem;
                }
                
                .form-control {
                    width: 100%;
                    padding: 0.75rem;
                    border: 2px solid #e9ecef;
                    border-radius: 6px;
                    font-size: 1rem;
                    transition: border-color 0.2s, box-shadow 0.2s;
                    box-sizing: border-box;
                }
                
                .form-control:focus {
                    outline: none;
                    border-color: #007bff;
                    box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
                }
                
                .checkbox-label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-weight: normal;
                }
                
                .checkbox-label input[type="checkbox"] {
                    margin-right: 0.5rem;
                }
                
                .form-actions {
                    display: flex;
                    gap: 1rem;
                    margin-top: 2rem;
                    flex-wrap: wrap;
                }
                
                .btn {
                    padding: 0.75rem 1.5rem;
                    border: 2px solid transparent;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                    text-align: center;
                    transition: all 0.2s;
                    flex: 1;
                    min-width: 120px;
                }
                
                .btn-primary {
                    background: #007bff;
                    color: white;
                }
                
                .btn-primary:hover {
                    background: #0056b3;
                    transform: translateY(-1px);
                }
                
                .btn-outline {
                    background: transparent;
                    border-color: #6c757d;
                    color: #6c757d;
                }
                
                .btn-outline:hover {
                    background: #6c757d;
                    color: white;
                    transform: translateY(-1px);
                }
                
                .contact-info {
                    margin-top: 3rem;
                    padding-top: 2rem;
                    border-top: 1px solid #e9ecef;
                }
                
                .contact-info h3 {
                    color: #2c3e50;
                    margin-bottom: 1.5rem;
                    text-align: center;
                }
                
                .contact-methods {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .contact-method {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 1rem;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
                
                .contact-icon {
                    font-size: 1.5rem;
                    width: 40px;
                    text-align: center;
                }
                
                .contact-method strong {
                    display: block;
                    color: #2c3e50;
                    margin-bottom: 0.25rem;
                }
                
                .contact-method p {
                    margin: 0;
                    color: #6c757d;
                    font-size: 0.9rem;
                }
                
                @media (max-width: 768px) {
                    .contact-form {
                        padding: 1rem;
                    }
                    
                    .form-container {
                        padding: 2rem;
                    }
                    
                    .form-actions {
                        flex-direction: column;
                    }
                    
                    .contact-methods {
                        gap: 0.5rem;
                    }
                    
                    .contact-method {
                        padding: 0.75rem;
                    }
                }
            `}</style>
        </div>
    );
}
module.exports = ContactForm;