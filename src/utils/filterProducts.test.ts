import { describe, expect, it } from "vitest";

import { PRODUCTS } from "../data/products";
import { filterProducts } from "./filterProducts";

describe("filterProducts", () => {
  it("returns all products when filters are empty", () => {
    expect(filterProducts(PRODUCTS, "", "All")).toHaveLength(5);
  });

  it("filters by search term", () => {
    const results = filterProducts(PRODUCTS, "SKU-002", "All");
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe("Safety Gloves");
  });

  it("filters by category", () => {
    const results = filterProducts(PRODUCTS, "", "Safety");
    expect(results).toHaveLength(2);
    expect(results.map((product) => product.name)).toEqual(["Safety Gloves", "Hard Hat"]);
  });
});
