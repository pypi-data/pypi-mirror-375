const React = require('react');

function ProductList({ products, categories, current_category, search_query, total_products, filtered_count }) {
    return (
        <div className="product-list">
            <header className="page-header">
                <h1>Products</h1>
                <div className="product-stats">
                    {filtered_count !== total_products ? (
                        <span>Showing {filtered_count} of {total_products} products</span>
                    ) : (
                        <span>{total_products} products</span>
                    )}
                </div>
            </header>
            
            {/* Filters */}
            <div className="filters">
                <div className="filter-group">
                    <label>Search:</label>
                    <input 
                        type="text" 
                        className="search-input"
                        placeholder="Search products..."
                        defaultValue={search_query || ''}
                    />
                </div>
                
                <div className="filter-group">
                    <label>Category:</label>
                    <select className="category-select" defaultValue={current_category || ''}>
                        <option value="">All Categories</option>
                        {categories && categories.map((category) => (
                            <option key={category} value={category}>
                                {category}
                            </option>
                        ))}
                    </select>
                </div>
                
                <button className="btn btn-primary">Apply Filters</button>
                {(current_category || search_query) && (
                    <a href="/products" className="btn btn-outline">Clear Filters</a>
                )}
            </div>
            
            {/* Products Grid */}
            {products && products.length > 0 ? (
                <div className="products-grid">
                    {products.map((product) => (
                        <div key={product.id} className="product-card">
                            <div className="product-image">
                                📦
                            </div>
                            <div className="product-info">
                                <h3 className="product-name">{product.name}</h3>
                                <p className="product-category">{product.category}</p>
                                <div className="product-price">
                                    ${product.price.toFixed(2)}
                                </div>
                            </div>
                            <div className="product-actions">
                                <button className="btn btn-primary btn-sm">View Details</button>
                                <button className="btn btn-outline btn-sm">Add to Cart</button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    {search_query || current_category ? (
                        <div>
                            <h3>No products found</h3>
                            <p>Try adjusting your search or filter criteria.</p>
                            <a href="/products" className="btn btn-primary">Show All Products</a>
                        </div>
                    ) : (
                        <div>
                            <h3>No products available</h3>
                            <p>Check back later for new products.</p>
                        </div>
                    )}
                </div>
            )}
            
            {/* Category Summary */}
            {categories && categories.length > 0 && (
                <div className="category-summary">
                    <h3>Browse by Category</h3>
                    <div className="category-tags">
                        {categories.map((category) => (
                            <a 
                                key={category} 
                                href={`?category=${encodeURIComponent(category)}`}
                                className={`category-tag ${current_category === category ? 'active' : ''}`}
                            >
                                {category}
                            </a>
                        ))}
                    </div>
                </div>
            )}
            
            <style jsx>{`
                .product-list {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }
                
                .page-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                }
                
                .page-header h1 {
                    color: #2c3e50;
                    margin: 0;
                }
                
                .product-stats {
                    color: #6c757d;
                    font-size: 0.9rem;
                }
                
                .filters {
                    display: flex;
                    gap: 1rem;
                    align-items: end;
                    background: white;
                    padding: 1.5rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                    flex-wrap: wrap;
                }
                
                .filter-group {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                
                .filter-group label {
                    font-weight: 600;
                    color: #495057;
                    font-size: 0.875rem;
                }
                
                .search-input,
                .category-select {
                    padding: 0.5rem;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    font-size: 0.9rem;
                    min-width: 200px;
                }
                
                .products-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 3rem;
                }
                
                .product-card {
                    background: white;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                
                .product-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
                
                .product-image {
                    font-size: 3rem;
                    text-align: center;
                    margin-bottom: 1rem;
                    color: #6c757d;
                }
                
                .product-name {
                    margin: 0 0 0.5rem 0;
                    color: #2c3e50;
                    font-size: 1.1rem;
                }
                
                .product-category {
                    color: #6c757d;
                    font-size: 0.875rem;
                    margin-bottom: 1rem;
                }
                
                .product-price {
                    font-size: 1.25rem;
                    font-weight: bold;
                    color: #28a745;
                    margin-bottom: 1rem;
                }
                
                .product-actions {
                    display: flex;
                    gap: 0.5rem;
                    flex-wrap: wrap;
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
                    transition: all 0.2s;
                }
                
                .btn-sm {
                    padding: 0.375rem 0.75rem;
                    font-size: 0.75rem;
                }
                
                .btn-primary {
                    background: #007bff;
                    color: white;
                }
                
                .btn-primary:hover {
                    background: #0056b3;
                }
                
                .btn-outline {
                    background: transparent;
                    border: 1px solid #6c757d;
                    color: #6c757d;
                }
                
                .btn-outline:hover {
                    background: #6c757d;
                    color: white;
                }
                
                .empty-state {
                    text-align: center;
                    padding: 4rem 2rem;
                    color: #6c757d;
                }
                
                .empty-state h3 {
                    color: #495057;
                    margin-bottom: 1rem;
                }
                
                .category-summary {
                    background: white;
                    padding: 2rem;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                
                .category-summary h3 {
                    margin: 0 0 1rem 0;
                    color: #2c3e50;
                }
                
                .category-tags {
                    display: flex;
                    gap: 0.5rem;
                    flex-wrap: wrap;
                }
                
                .category-tag {
                    padding: 0.5rem 1rem;
                    background: #f8f9fa;
                    color: #495057;
                    text-decoration: none;
                    border-radius: 20px;
                    border: 1px solid #dee2e6;
                    font-size: 0.875rem;
                    transition: all 0.2s;
                }
                
                .category-tag:hover,
                .category-tag.active {
                    background: #007bff;
                    color: white;
                    border-color: #007bff;
                }
                
                @media (max-width: 768px) {
                    .filters {
                        flex-direction: column;
                        align-items: stretch;
                    }
                    
                    .filter-group {
                        flex-direction: row;
                        align-items: center;
                        justify-content: space-between;
                    }
                    
                    .search-input,
                    .category-select {
                        min-width: auto;
                        flex: 1;
                        margin-left: 1rem;
                    }
                }
            `}</style>
        </div>
    );
}

module.exports = ProductList;