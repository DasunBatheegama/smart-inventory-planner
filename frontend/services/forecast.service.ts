import {
  ForecastResult,
  ForecastAccuracy,
  ForecastData,
  GrowthProduct,
  RiskProduct,
  ForecastSummary,
  ForecastControls,
} from "@/types/forecast";
import {
  mockForecastData,
  mockForecastProjection,
  mockForecastResults,
  mockGrowthProducts,
  mockRiskProducts,
  mockForecastAccuracy,
  mockForecastSummary,
} from "@/data/mock-forecast";

class ForecastService {
  async generateForecast(controls: ForecastControls): Promise<{
    historical: ForecastData[];
    projection: ForecastData[];
  }> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const projection = mockForecastProjection.slice(0, controls.horizon);
        resolve({ historical: [...mockForecastData], projection });
      }, 600)
    );
  }

  async getForecastResults(): Promise<ForecastResult[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockForecastResults]), 300)
    );
  }

  async getForecastAccuracy(): Promise<ForecastAccuracy> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockForecastAccuracy }), 300)
    );
  }

  async getGrowthProducts(): Promise<GrowthProduct[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockGrowthProducts]), 300)
    );
  }

  async getRiskProducts(): Promise<RiskProduct[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockRiskProducts]), 300)
    );
  }

  async getForecastSummary(): Promise<ForecastSummary> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockForecastSummary }), 300)
    );
  }

  async exportForecast(): Promise<string> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const header = "Month,Forecast Quantity,Confidence,Method";
        const rows = mockForecastResults
          .map(
            (r) =>
              `${r.month},${r.forecastQuantity},${r.confidence}%,${r.method}`
          )
          .join("\n");
        resolve(`${header}\n${rows}`);
      }, 400)
    );
  }
}

export const forecastService = new ForecastService();
