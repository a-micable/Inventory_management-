export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  unitPrice: number;
  stock: number;
}

export const PRODUCTS: Product[] = [
  {
    id: "1",
    sku: "SKU-001",
    name: "Adjustable Wrench",
    category: "Tools",
    unitPrice: 24.99,
    stock: 45,
  },
  {
    id: "2",
    sku: "SKU-002",
    name: "Safety Gloves",
    category: "Safety",
    unitPrice: 12.5,
    stock: 120,
  },
  {
    id: "3",
    sku: "SKU-003",
    name: "Cordless Drill",
    category: "Tools",
    unitPrice: 89.99,
    stock: 18,
  },
  {
    id: "4",
    sku: "SKU-004",
    name: "Hard Hat",
    category: "Safety",
    unitPrice: 19.75,
    stock: 60,
  },
  {
    id: "5",
    sku: "SKU-005",
    name: "Measuring Tape",
    category: "Tools",
    unitPrice: 8.99,
    stock: 200,
  },
];
