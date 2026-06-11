import { Product } from '../types/product';

export const mockProducts: Product[] = [
  {
    id: "1",
    sku: "SKU-1001",
    name: "Wireless Mouse",
    category: "Electronics",
    currentStock: 120,
    unitCost: 15,
    leadTime: 7,
    supplier: "ABC Supplies",
    reorderPoint: 50,
    safetyStock: 20,
    status: "in-stock"
  },
  {
    id: "2",
    sku: "SKU-1002",
    name: "Mechanical Keyboard",
    category: "Electronics",
    currentStock: 15,
    unitCost: 65,
    leadTime: 14,
    supplier: "TechCorp",
    reorderPoint: 20,
    safetyStock: 10,
    status: "low-stock"
  },
  {
    id: "3",
    sku: "SKU-1003",
    name: "Office Chair",
    category: "Furniture",
    currentStock: 0,
    unitCost: 120,
    leadTime: 21,
    supplier: "FurniCo",
    reorderPoint: 10,
    safetyStock: 5,
    status: "out-of-stock"
  },
  {
    id: "4",
    sku: "SKU-1004",
    name: "USB-C Hub",
    category: "Electronics",
    currentStock: 300,
    unitCost: 25,
    leadTime: 5,
    supplier: "TechCorp",
    reorderPoint: 100,
    safetyStock: 30,
    status: "in-stock"
  },
  {
    id: "5",
    sku: "SKU-1005",
    name: "Standing Desk",
    category: "Furniture",
    currentStock: 8,
    unitCost: 350,
    leadTime: 30,
    supplier: "FurniCo",
    reorderPoint: 15,
    safetyStock: 5,
    status: "low-stock"
  }
];
