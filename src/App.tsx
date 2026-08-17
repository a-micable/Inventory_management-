import { ProductCatalog } from "./components/ProductCatalog";
import { PRODUCTS } from "./data/products";
import "./index.css";

export default function App() {
  return (
    <main>
      <ProductCatalog products={PRODUCTS} />
    </main>
  );
}
