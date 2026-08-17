import type { Product } from "../data/products";

export function filterProducts(
  products: Product[],
  searchTerm: string,
  category: string,
): Product[] {
  const normalizedSearch = searchTerm.trim().toLowerCase();

  return products.filter((product) => {
    const matchesCategory = category === "All" || product.category === category;
    const matchesSearch =
      normalizedSearch === "" ||
      product.name.toLowerCase().includes(normalizedSearch) ||
      product.sku.toLowerCase().includes(normalizedSearch);

    return matchesCategory && matchesSearch;
  });
}
