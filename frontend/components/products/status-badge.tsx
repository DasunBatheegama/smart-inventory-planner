import { Badge } from "@/components/ui/badge";
import { ProductStatus } from "@/types/product";

interface StatusBadgeProps {
  status: ProductStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  switch (status) {
    case "in-stock":
      return <Badge variant="default" className="bg-emerald-500 hover:bg-emerald-600">In Stock</Badge>;
    case "low-stock":
      return <Badge variant="secondary" className="bg-yellow-500 text-white hover:bg-yellow-600">Low Stock</Badge>;
    case "out-of-stock":
      return <Badge variant="destructive">Out of Stock</Badge>;
    default:
      return <Badge variant="outline">Unknown</Badge>;
  }
}
