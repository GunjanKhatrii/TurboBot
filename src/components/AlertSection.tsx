import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle, AlertCircle } from "lucide-react";
import { TurbineAlert } from "@/lib/turbineData";

interface AlertSectionProps {
  alerts: TurbineAlert[];
}

export const AlertSection = ({ alerts }: AlertSectionProps) => {
  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No active alerts. System operating normally.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Active Alerts</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {alerts.map((alert) => (
          <Alert 
            key={alert.id} 
            variant={alert.severity === 'critical' ? 'destructive' : 'default'}
            className={alert.severity === 'warning' ? 'border-warning bg-warning/10' : ''}
          >
            {alert.severity === 'critical' ? (
              <AlertCircle className="h-4 w-4" />
            ) : (
              <AlertTriangle className="h-4 w-4" />
            )}
            <AlertTitle className="text-sm font-semibold">
              {alert.severity === 'critical' ? 'Critical' : 'Warning'}
            </AlertTitle>
            <AlertDescription className="text-xs">
              {alert.message}
            </AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  );
};
