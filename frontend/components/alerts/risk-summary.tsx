"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";
import { AlertCategoryData } from "@/types/alert";
import { BarChart3 } from "lucide-react";

interface RiskSummaryProps {
  categoryData: AlertCategoryData[];
  severityData: AlertCategoryData[];
}

export function RiskSummary({ categoryData, severityData }: RiskSummaryProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Inventory Risk Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-xs font-medium text-muted-foreground mb-2 text-center">
              By Category
            </h4>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={35}
                  outerRadius={60}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {categoryData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Legend
                  wrapperStyle={{ fontSize: 10 }}
                  iconSize={8}
                  formatter={(value) => (
                    <span className="text-muted-foreground">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div>
            <h4 className="text-xs font-medium text-muted-foreground mb-2 text-center">
              By Severity
            </h4>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={35}
                  outerRadius={60}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {severityData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Legend
                  wrapperStyle={{ fontSize: 10 }}
                  iconSize={8}
                  formatter={(value) => (
                    <span className="text-muted-foreground">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
