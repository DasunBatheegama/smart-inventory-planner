import { Product } from '../types/product';
import { mockProducts } from '../data/mock-products';

// Service placeholder for future backend integration
class ProductService {
  private products: Product[] = [...mockProducts];

  async getProducts(): Promise<Product[]> {
    return new Promise((resolve) => setTimeout(() => resolve([...this.products]), 300));
  }

  async getProductById(id: string): Promise<Product | undefined> {
    return new Promise((resolve) => setTimeout(() => {
      resolve(this.products.find(p => p.id === id));
    }, 200));
  }

  async createProduct(product: Omit<Product, 'id' | 'status'>): Promise<Product> {
    return new Promise((resolve) => setTimeout(() => {
      const newProduct: Product = {
        ...product,
        id: Math.random().toString(36).substring(7),
        status: this.calculateStatus(product.currentStock, product.reorderPoint)
      };
      
      this.products.push(newProduct);
      resolve(newProduct);
    }, 400));
  }

  async updateProduct(id: string, updates: Partial<Product>): Promise<Product | undefined> {
    return new Promise((resolve) => setTimeout(() => {
      const index = this.products.findIndex(p => p.id === id);
      if (index === -1) return resolve(undefined);
      
      const updatedProduct = { ...this.products[index], ...updates };
      
      if (updates.currentStock !== undefined || updates.reorderPoint !== undefined) {
        updatedProduct.status = this.calculateStatus(updatedProduct.currentStock, updatedProduct.reorderPoint);
      }
      
      this.products[index] = updatedProduct;
      resolve(updatedProduct);
    }, 400));
  }

  async deleteProduct(id: string): Promise<boolean> {
    return new Promise((resolve) => setTimeout(() => {
      const initialLength = this.products.length;
      this.products = this.products.filter(p => p.id !== id);
      resolve(this.products.length < initialLength);
    }, 300));
  }

  private calculateStatus(currentStock: number, reorderPoint: number): Product['status'] {
    if (currentStock === 0) return 'out-of-stock';
    if (currentStock <= reorderPoint) return 'low-stock';
    return 'in-stock';
  }
}

export const productService = new ProductService();
