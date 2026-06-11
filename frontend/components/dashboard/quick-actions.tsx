import * as React from "react";
import { Plus, Upload, LineChart } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function QuickActions() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        <Button className="w-full justify-start" variant="outline">
          <Plus className="mr-2 h-4 w-4" />
          Add Product
        </Button>
        <Button className="w-full justify-start" variant="outline">
          <Upload className="mr-2 h-4 w-4" />
          Upload Sales Data
        </Button>
        <Button className="w-full justify-start" variant="outline">
          <LineChart className="mr-2 h-4 w-4" />
          Generate Forecast
        </Button>
      </CardContent>
    </Card>
  );
}