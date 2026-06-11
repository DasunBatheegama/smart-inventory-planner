import {
  InventoryPlanItem,
  InventoryMetrics,
  InventoryHealth,
  RiskProduct,
  Recommendation,
  PurchasePlan,
  TrendDataPoint,
  InventoryFilters,
} from "@/types/inventory";
import {
  mockInventoryPlan,
  mockInventoryMetrics,
  mockInventoryHealth,
  mockRiskProducts,
  mockRecommendations,
  mockPurchasePlans,
  mockTrendData,
} from "@/data/mock-inventory";

class InventoryService {
  async calculateInventoryPlan(
    filters?: InventoryFilters
  ): Promise<InventoryPlanItem[]> {
    return new Promise((resolve) =>
      setTimeout(() => {
        let data = [...mockInventoryPlan];
        if (filters) {
          if (filters.product && filters.product !== "all") {
            data = data.filter((p) => p.sku === filters.product);
          }
          if (filters.category && filters.category !== "All Categories") {
            data = data.filter((p) => p.category === filters.category);
          }
          if (filters.supplier && filters.supplier !== "All Suppliers") {
            data = data.filter((p) => p.supplier === filters.supplier);
          }
          if (filters.status && filters.status !== "all") {
            data = data.filter((p) => p.status === filters.status);
          }
        }
        resolve(data);
      }, 400)
    );
  }

  async getInventoryMetrics(): Promise<InventoryMetrics> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockInventoryMetrics }), 300)
    );
  }

  async getInventoryHealth(): Promise<InventoryHealth> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockInventoryHealth }), 300)
    );
  }

  async getRiskProducts(): Promise<RiskProduct[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockRiskProducts]), 300)
    );
  }

  async getRecommendations(): Promise<Recommendation[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockRecommendations]), 300)
    );
  }

  async getPurchasePlans(): Promise<PurchasePlan[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockPurchasePlans]), 300)
    );
  }

  async getTrendData(): Promise<TrendDataPoint[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockTrendData]), 300)
    );
  }

  async exportPlan(): Promise<string> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const header =
          "SKU,Product Name,Current Stock,Forecast Demand,Safety Stock,Reorder Point,EOQ,Recommended Order,Status";
        const rows = mockInventoryPlan
          .map(
            (p) =>
              `${p.sku},${p.productName},${p.currentStock},${p.forecastDemand},${p.safetyStock},${p.reorderPoint},${p.eoq},${p.recommendedOrder},${p.status}`
          )
          .join("\n");
        resolve(`${header}\n${rows}`);
      }, 400)
    );
  }
}

export const inventoryService = new InventoryService();
