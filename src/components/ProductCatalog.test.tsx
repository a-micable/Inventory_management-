import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ProductCatalog } from "./ProductCatalog";
import { PRODUCTS } from "../data/products";

describe("ProductCatalog", () => {
  it("shows all products initially", () => {
    render(<ProductCatalog products={PRODUCTS} />);

    expect(screen.getByText(/5 products shown/i)).toBeTruthy();
    expect(screen.getByText(/Adjustable Wrench/i)).toBeTruthy();
    expect(screen.getByText(/Hard Hat/i)).toBeTruthy();
  });

  it("updates the list when the user searches by SKU", async () => {
    const user = userEvent.setup();
    render(<ProductCatalog products={PRODUCTS} />);

    await user.type(screen.getByLabelText(/search/i), "SKU-003");

    expect(screen.getByText(/1 products shown/i)).toBeTruthy();
    expect(screen.getByText(/Cordless Drill/i)).toBeTruthy();
    expect(screen.queryByText(/Adjustable Wrench/i)).toBeNull();
  });

  it("updates the list when the category filter changes", async () => {
    const user = userEvent.setup();
    render(<ProductCatalog products={PRODUCTS} />);

    await user.selectOptions(screen.getByLabelText(/category/i), "Safety");

    expect(screen.getByText(/2 products shown/i)).toBeTruthy();
    expect(screen.getByText(/Safety Gloves/i)).toBeTruthy();
    expect(screen.getByText(/Hard Hat/i)).toBeTruthy();
    expect(screen.queryByText(/Cordless Drill/i)).toBeNull();
  });

  it("combines search and category filters", async () => {
    const user = userEvent.setup();
    render(<ProductCatalog products={PRODUCTS} />);

    await user.selectOptions(screen.getByLabelText(/category/i), "Tools");
    await user.type(screen.getByLabelText(/search/i), "wrench");

    expect(screen.getByText(/1 products shown/i)).toBeTruthy();
    expect(screen.getByText(/Adjustable Wrench/i)).toBeTruthy();
    expect(screen.queryByText(/Cordless Drill/i)).toBeNull();
  });
});
