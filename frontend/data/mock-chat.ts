import {
  Conversation,
  AiMetrics,
  InventorySummary,
  AiRecommendation,
  ChatMessage,
} from "@/types/chat";

function msg(
  id: string,
  role: "user" | "assistant",
  content: string,
  minutesAgo: number
): ChatMessage {
  const date = new Date(Date.now() - minutesAgo * 60 * 1000);
  return { id, role, content, createdAt: date.toISOString() };
}

export const mockConversations: Conversation[] = [
  {
    id: "conv-1",
    title: "Which products need reordering?",
    lastMessage: "Based on current stock levels and reorder points...",
    updatedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    messages: [
      msg("m1", "user", "Which products need reordering?", 35),
      msg(
        "m2",
        "assistant",
        `Based on current stock levels and reorder point calculations, here are the products that need reordering:

| Product | SKU | Current Stock | Reorder Point | Recommended Order |
|---|---|---|---|---|
| Standing Desk | SKU-1004 | 320 | 285 | 630 |
| Desk Lamp | SKU-1008 | 180 | 360 | 1,020 |
| Ergonomic Chair | SKU-1002 | 410 | 315 | 640 |
| Smart Power Strip | SKU-1011 | 450 | 330 | 650 |
| Monitor Arm | SKU-1006 | 890 | 540 | 910 |
| USB-C Hub | SKU-1005 | 1,350 | 660 | 850 |
| Wireless Headphones | SKU-1001 | 1,200 | 555 | 650 |

**Key recommendations:**
- **Desk Lamp (SKU-1008)** has the most urgent need — only 180 units with a reorder point of 360 and 5 days of stock remaining.
- **Standing Desk (SKU-1004)** is also critical with 320 units and 10 days remaining.
- Place these orders within the next 3 days to avoid stockouts.`,
        35
      ),
    ],
  },
  {
    id: "conv-2",
    title: "What are my biggest inventory risks?",
    lastMessage: "Let me analyze your current inventory data...",
    updatedAt: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
    messages: [
      msg("m3", "user", "What are my biggest inventory risks?", 125),
      msg(
        "m4",
        "assistant",
        `Here's my analysis of your current inventory risks:

## Stockout Risks (High Priority)
| Product | SKU | Days Remaining | Risk Level |
|---|---|---|---|
| Desk Lamp | SKU-1008 | 5 days | **Critical** |
| Standing Desk | SKU-1004 | 10 days | **High** |
| Ergonomic Chair | SKU-1002 | 12 days | **High** |

## Overstock Risks
| Product | SKU | Current Stock | Excess % |
|---|---|---|---|
| Cable Management Kit | SKU-1012 | 2,800 units | 250% above demand |
| Noise Cancelling Earbuds | SKU-1007 | 2,300 units | 59% above demand |

## Slow Moving Inventory
- **Monitor Arm (SKU-1006)** — Turnover dropped 40%
- **Smart Power Strip (SKU-1011)** — Below turnover threshold

**Immediate actions recommended:**
1. Place orders for Desk Lamp and Standing Desk within 48 hours
2. Schedule a promotion for Cable Management Kit to reduce excess stock
3. Review Monitor Arm pricing strategy`,
        125
      ),
    ],
  },
  {
    id: "conv-3",
    title: "Explain forecast accuracy",
    lastMessage: "Your forecast is currently using Exponential Smoothing...",
    updatedAt: new Date(Date.now() - 300 * 60 * 1000).toISOString(),
    messages: [
      msg("m5", "user", "Explain forecast accuracy", 305),
      msg(
        "m6",
        "assistant",
        `## Forecast Accuracy Report

Your current forecast model is performing well with the following metrics:

| Metric | Value | Rating |
|---|---|---|
| MAPE (Mean Absolute Percentage Error) | 7.2% | **Good** |
| MAE (Mean Absolute Error) | 142 units | **Good** |
| Confidence Score | 88% | **Good** |

**Method used:** Exponential Smoothing

### Performance by Horizon
- **1-3 months:** 92% confidence — Excellent short-term accuracy
- **4-6 months:** 82% confidence — Good medium-term reliability
- **7-12 months:** 65-70% confidence — Decreasing accuracy at longer horizons

### Recommendations
1. Forecast accuracy is sufficient for operational planning (30-90 day horizon)
2. Consider incorporating seasonal adjustments for Q4 holiday demand
3. Re-evaluate forecast model if MAPE exceeds 10%`,
        305
      ),
    ],
  },
];

export const mockAiMetrics: AiMetrics = {
  totalProductsAnalyzed: 12,
  activeAlerts: 14,
  inventoryHealthScore: 72,
  forecastAccuracy: 88,
};

export const mockInventorySummary: InventorySummary = {
  totalProducts: 12,
  inventoryValue: 284500,
  activeAlerts: 14,
  reorderRequired: 7,
};

export const mockAiRecommendations: AiRecommendation[] = [
  {
    id: "ai-rec-1",
    sku: "SKU-1004",
    productName: "Standing Desk",
    action: "Reorder SKU-1004 within 3 days — only 10 days of stock remaining.",
    daysUntilAction: 3,
  },
  {
    id: "ai-rec-2",
    sku: "SKU-1008",
    productName: "Desk Lamp",
    action: "Place urgent order for 1,020 units of SKU-1008 — critically low.",
    daysUntilAction: 2,
  },
  {
    id: "ai-rec-3",
    sku: "SKU-1002",
    productName: "Ergonomic Chair",
    action: "Order 640 units of SKU-1002 to replenish above reorder point.",
    daysUntilAction: 5,
  },
  {
    id: "ai-rec-4",
    sku: "SKU-1012",
    productName: "Cable Management Kit",
    action: "Reduce purchasing for SKU-1012 — excess stock of 2,800 units.",
    daysUntilAction: 30,
  },
  {
    id: "ai-rec-5",
    sku: "SKU-1005",
    productName: "USB-C Hub",
    action: "Increase safety stock for SKU-1005 due to extended supplier lead times.",
    daysUntilAction: 10,
  },
];

export const mockQuickResponses: {
  keywords: string[];
  response: string;
}[] = [
  {
    keywords: ["reorder", "reorder", "order", "purchase"],
    response: `Based on current stock levels and reorder point calculations, here are the products that need reordering:

| Product | SKU | Current Stock | Reorder Point | Recommended Order |
|---|---|---|---|---|
| Standing Desk | SKU-1004 | 320 | 285 | 630 |
| Desk Lamp | SKU-1008 | 180 | 360 | 1,020 |
| Ergonomic Chair | SKU-1002 | 410 | 315 | 640 |
| Smart Power Strip | SKU-1011 | 450 | 330 | 650 |
| Monitor Arm | SKU-1006 | 890 | 540 | 910 |

**Recommended action:** Place orders for Desk Lamp and Standing Desk within 48 hours — they have the most critical stock levels.`,
  },
  {
    keywords: ["risk", "risk", "danger", "threat"],
    response: `Here are your biggest inventory risks:

**Stockout Risks (Critical)**
- **Desk Lamp (SKU-1008):** Only 5 days of stock remaining — **highest risk**
- **Standing Desk (SKU-1004):** 10 days remaining — place order now
- **Ergonomic Chair (SKU-1002):** 12 days remaining — schedule this week

**Overstock Risks**
- **Cable Management Kit (SKU-1012):** 2,800 units — 250% above demand
- **Noise Cancelling Earbuds (SKU-1007):** 2,300 units — 59% above demand

**Slow Moving**
- Monitor Arm and Smart Power Strip showing declining turnover rates.

Your most urgent risk is the **Desk Lamp** which will stock out in 5 days.`,
  },
  {
    keywords: ["forecast", "accuracy", "mape", "confidence"],
    response: `## Forecast Accuracy

Your Exponential Smoothing model is performing well:

| Metric | Value | Rating |
|---|---|---|
| MAPE | 7.2% | Good |
| MAE | 142 units | Good |
| Confidence Score | 88% | Good |

**Horizon breakdown:**
- **1-3 months:** 92% confidence
- **4-6 months:** 82% confidence  
- **7-12 months:** 65-70% confidence

Forecast is reliable for 30-90 day planning. Consider seasonal adjustments for Q4.`,
  },
  {
    keywords: ["low stock", "low stock", "shortage", "running out"],
    response: `## Products at Risk of Stockout

| Product | SKU | Current Stock | Days Remaining |
|---|---|---|---|
| Desk Lamp | SKU-1008 | 180 | **5 days** |
| Standing Desk | SKU-1004 | 320 | **10 days** |
| Ergonomic Chair | SKU-1002 | 410 | **12 days** |
| Smart Power Strip | SKU-1011 | 450 | **12 days** |
| Monitor Arm | SKU-1006 | 890 | **15 days** |
| Wireless Headphones | SKU-1001 | 1,200 | **19 days** |

Products with fewer than 10 days of stock require immediate attention.`,
  },
  {
    keywords: ["summary", "summarize", "overview", "all alerts"],
    response: `## Active Alerts Summary

You have **14 active alerts**:

- **5 Critical** — Require immediate action
- **5 Warning** — Require attention this week
- **4 Info** — Monitor and plan ahead

**Breakdown by type:**
- Stockout Risk: 3 alerts
- Low Stock: 2 alerts
- Reorder Required: 3 alerts
- Overstock: 3 alerts
- Slow Moving: 2 alerts
- Forecast Anomaly: 1 alert

**Top priority:** Desk Lamp (SKU-1008) and Standing Desk (SKU-1004) need orders placed immediately.`,
  },
  {
    keywords: ["grow", "growth", "growing", "top product"],
    response: `## Top Growth Products

Based on forecast demand projections, these products show the highest growth:

| Product | Current Demand | Forecast Demand | Growth |
|---|---|---|---|
| Noise Cancelling Earbuds | 850 | 1,450 | **+70.6%** |
| Wireless Headphones | 1,200 | 1,850 | **+54.2%** |
| Webcam 4K | 620 | 950 | **+53.2%** |
| Mechanical Keyboard | 1,100 | 1,550 | **+40.9%** |
| Ergonomic Chair | 780 | 1,050 | **+34.6%** |

**Action:** Ensure sufficient safety stock for these products to capture the forecasted growth.`,
  },
];
