import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TurbineDataPoint } from "@/lib/turbineData";

interface WindPowerScatterProps {
  data: TurbineDataPoint[];
}

export const WindPowerScatter = ({ data }: WindPowerScatterProps) => {
  const scatterData = data.map(point => ({
    windSpeed: point.wind_speed,
    power: point.power_output,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Wind Speed vs Power Output</CardTitle>
        <CardDescription>Power curve analysis</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="windSpeed" 
              name="Wind Speed"
              unit=" m/s"
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              label={{ value: 'Wind Speed (m/s)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              dataKey="power" 
              name="Power"
              unit=" kW"
              className="text-xs"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              label={{ value: 'Power (kW)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ 
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
            />
            <Scatter 
              data={scatterData} 
              fill="hsl(var(--chart-2))"
            />
          </ScatterChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
