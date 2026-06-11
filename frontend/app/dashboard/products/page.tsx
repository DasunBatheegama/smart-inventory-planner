"use client";

import { useEffect, useState, useMemo } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProductStats } from "@/components/products/product-stats";
import { ProductFilters } from "@/components/products/product-filters";
import { ProductsTable } from "@/components/products/products-table";
import { ProductDetails } from "@/components/products/product-details";
import { ProductForm } from "@/components/products/product-form";
import { DeleteProductDialog } from "@/components/products/delete-product-dialog";
import { Product } from "@/types/product";
import { productService } from "@/services/product.service";
import { ProductFormValues } from "@/types/product-form";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // Modals / Drawers state
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editProductId, setEditProductId] = useState<string | null>(null);
  const [viewProductId, setViewProductId] = useState<string | null>(null);
  const [deleteProductId, setDeleteProductId] = useState<string | null>(null);
  
  // Action loading state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await productService.getProducts();
      setProducts(data);
    } catch (error) {
      console.error("Failed to load products:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesSearch = 
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        p.sku.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = statusFilter === "all" || p.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [products, searchQuery, statusFilter]);

  const handleAddSubmit = async (data: ProductFormValues) => {
    setIsSubmitting(true);
    try {
      await productService.createProduct(data as Omit<Product, 'id' | 'status'>);
      await loadProducts();
      setIsAddOpen(false);
    } catch (error) {
      console.error("Error creating product:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditSubmit = async (data: ProductFormValues) => {
    if (!editProductId) return;
    setIsSubmitting(true);
    try {
      await productService.updateProduct(editProductId, data);
      await loadProducts();
      setEditProductId(null);
    } catch (error) {
      console.error("Error updating product:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteProductId) return;
    setIsDeleting(true);
    try {
      await productService.deleteProduct(deleteProductId);
      await loadProducts();
      setDeleteProductId(null);
    } catch (error) {
      console.error("Error deleting product:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const productToEdit = products.find(p => p.id === editProductId);
  const productToView = products.find(p => p.id === viewProductId);
  const productToDelete = products.find(p => p.id === deleteProductId);

  return (
    <div className="flex-1 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Products</h2>
          <p className="text-muted-foreground mt-1">Manage your inventory catalog and stock information</p>
        </div>
        <Button onClick={() => setIsAddOpen(true)}>
          <Plus className="mr-2 h-4 w-4" /> Add Product
        </Button>
      </div>

      <ProductStats products={products} />

      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6 mt-4 opacity-100">
        <ProductFilters 
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
        />
        
        {loading ? (
          <div className="h-64 flex items-center justify-center text-muted-foreground">Loading products...</div>
        ) : (
          <ProductsTable 
            data={filteredProducts} 
            onView={(id) => setViewProductId(id)}
            onEdit={(id) => setEditProductId(id)}
            onDelete={(id) => setDeleteProductId(id)}
          />
        )}
      </div>

      {/* Add Product Dialog */}
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Add New Product</DialogTitle>
          </DialogHeader>
          <ProductForm 
            onSubmit={handleAddSubmit} 
            onCancel={() => setIsAddOpen(false)}
            isLoading={isSubmitting}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Product Dialog */}
      <Dialog open={!!editProductId} onOpenChange={(open) => !open && setEditProductId(null)}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
          </DialogHeader>
          {productToEdit && (
            <ProductForm 
              initialValues={productToEdit}
              onSubmit={handleEditSubmit} 
              onCancel={() => setEditProductId(null)}
              isLoading={isSubmitting}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Product Config */}
      <DeleteProductDialog 
        open={!!deleteProductId}
        onOpenChange={(open) => !open && setDeleteProductId(null)}
        onConfirm={handleDeleteConfirm}
        productName={productToDelete?.name}
        isDeleting={isDeleting}
      />

      {/* View Product Drawer */}
      <ProductDetails 
        open={!!viewProductId}
        onOpenChange={(open) => !open && setViewProductId(null)}
        product={productToView || null}
      />
    </div>
  );
}
