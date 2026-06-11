import {
  Alert,
  AlertMetrics,
  AlertCategoryData,
  Recommendation,
  AlertFilters,
} from "@/types/alert";
import {
  mockAlerts,
  mockAlertMetrics,
  mockAlertCategoryData,
  mockAlertSeverityData,
  mockRecommendations,
} from "@/data/mock-alerts";

class AlertService {
  private alerts: Alert[] = [...mockAlerts];

  async getAlerts(filters?: AlertFilters): Promise<Alert[]> {
    return new Promise((resolve) =>
      setTimeout(() => {
        let data = [...this.alerts];
        if (filters) {
          if (filters.type && filters.type !== "all") {
            data = data.filter((a) => a.type === filters.type);
          }
          if (filters.severity && filters.severity !== "all") {
            data = data.filter((a) => a.severity === filters.severity);
          }
          if (filters.product && filters.product !== "all") {
            data = data.filter((a) => a.sku === filters.product);
          }
          if (filters.supplier && filters.supplier !== "All Suppliers") {
            data = data.filter((a) => a.supplier === filters.supplier);
          }
          if (filters.dateRange && filters.dateRange !== "all") {
            const now = new Date();
            const cutoff = new Date();
            if (filters.dateRange === "today") cutoff.setHours(0, 0, 0, 0);
            else if (filters.dateRange === "7d") cutoff.setDate(now.getDate() - 7);
            else if (filters.dateRange === "30d") cutoff.setDate(now.getDate() - 30);
            data = data.filter((a) => new Date(a.createdAt) >= cutoff);
          }
          if (filters.search) {
            const q = filters.search.toLowerCase();
            data = data.filter(
              (a) =>
                a.productName.toLowerCase().includes(q) ||
                a.sku.toLowerCase().includes(q) ||
                a.message.toLowerCase().includes(q)
            );
          }
        }
        resolve(data);
      }, 400)
    );
  }

  async getAlertMetrics(): Promise<AlertMetrics> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const active = this.alerts.filter((a) => a.status !== "resolved");
        resolve({
          totalActive: active.length,
          criticalCount: active.filter((a) => a.severity === "critical").length,
          reorderRequired: active.filter((a) => a.type === "reorder-required").length,
          overstockWarnings: active.filter((a) => a.type === "overstock").length,
        });
      }, 300)
    );
  }

  async getAlertCategoryData(): Promise<AlertCategoryData[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockAlertCategoryData]), 300)
    );
  }

  async getAlertSeverityData(): Promise<AlertCategoryData[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockAlertSeverityData]), 300)
    );
  }

  async getAlertTimeline(): Promise<Alert[]> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const sorted = [...this.alerts].sort(
          (a, b) =>
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );
        resolve(sorted.slice(0, 10));
      }, 300)
    );
  }

  async getRecommendations(): Promise<Recommendation[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockRecommendations]), 300)
    );
  }

  async markAsRead(id: string): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const alert = this.alerts.find((a) => a.id === id);
        if (alert && alert.status === "new") {
          alert.status = "acknowledged";
        }
        resolve();
      }, 200)
    );
  }

  async markAllAsRead(): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        this.alerts.forEach((a) => {
          if (a.status === "new") a.status = "acknowledged";
        });
        resolve();
      }, 300)
    );
  }

  async resolveAlert(id: string): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const alert = this.alerts.find((a) => a.id === id);
        if (alert) alert.status = "resolved";
        resolve();
      }, 200)
    );
  }

  async exportAlerts(): Promise<string> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const header =
          "ID,Type,Severity,SKU,Product,Status,Message,Created";
        const rows = this.alerts
          .map(
            (a) =>
              `${a.id},${a.type},${a.severity},${a.sku},${a.productName},${a.status},"${a.message}",${a.createdAt}`
          )
          .join("\n");
        resolve(`${header}\n${rows}`);
      }, 400)
    );
  }
}

export const alertService = new AlertService();
