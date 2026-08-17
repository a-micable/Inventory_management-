import { useEffect, useState } from "react";

import type { Product } from "../data/products";
import { filterProducts } from "../utils/filterProducts";

interface ProductCatalogProps {
  products: Product[];
}

export function ProductCatalog({ products }: ProductCatalogProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("All");
  const [filteredProducts, setFilteredProducts] = useState<Product[]>(products);

  useEffect(() => {
    setFilteredProducts(filterProducts(products, searchTerm, category));
  }, []);

  const categories = ["All", ...new Set(products.map((product) => product.category))];

  return (
    <section aria-label="Product catalog">
      <header>
        <h1>Product Catalog</h1>
        <p>{filteredProducts.length} products shown</p>
      </header>

      <div className="filters">
        <label htmlFor="product-search">Search</label>
        <input
          id="product-search"
          type="search"
          placeholder="Search by name or SKU"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
        />

        <label htmlFor="product-category">Category</label>
        <select
          id="product-category"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
        >
          {categories.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>

      <ul>
        {filteredProducts.map((product) => (
          <li key={product.id}>
            <strong>{product.name}</strong> ({product.sku}) — {product.category} — $
            {product.unitPrice.toFixed(2)} — {product.stock} in stock
          </li>
        ))}
      </ul>
    </section>
  );
}
