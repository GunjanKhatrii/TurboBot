export interface TurbineDataPoint {
  timestamp: string;
  wind_speed: number;
  power_output: number;
  temperature: number;
  vibration: number;
  status: 'operating' | 'warning' | 'offline';
}

export interface TurbineAlert {
  id: string;
  type: 'high_temp' | 'high_vibration' | 'low_performance';
  severity: 'warning' | 'critical';
  message: string;
  timestamp: string;
}

// Generate realistic sample data for wind turbine
export function generateTurbineData(): TurbineDataPoint[] {
  const data: TurbineDataPoint[] = [];
  const now = new Date();
  
  for (let i = 47; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
    
    // Simulate wind speed variations
    const baseWindSpeed = 8 + Math.sin(i / 8) * 3;
    const windSpeed = Math.max(3, Math.min(15, baseWindSpeed + (Math.random() - 0.5) * 2));
    
    // Power output follows cubic relationship with wind speed, with some degradation in later hours
    const degradationFactor = i < 12 ? 0.85 : 1.0;
    const idealPower = Math.pow(windSpeed / 12, 3) * 2000 * degradationFactor;
    const powerOutput = Math.max(0, Math.min(2000, idealPower + (Math.random() - 0.5) * 100));
    
    // Temperature increases with power output and time
    const baseTemp = 35 + (powerOutput / 2000) * 30;
    const temperature = i < 15 ? baseTemp + 15 : baseTemp;
    
    // Vibration increases with issues
    const baseVibration = 1.0 + (powerOutput / 2000) * 2;
    const vibration = i < 15 ? baseVibration + 2.5 : baseVibration;
    
    // Status determination
    let status: 'operating' | 'warning' | 'offline' = 'operating';
    if (temperature > 70 || vibration > 4.0) {
      status = 'warning';
    }
    
    data.push({
      timestamp: timestamp.toISOString(),
      wind_speed: Math.round(windSpeed * 10) / 10,
      power_output: Math.round(powerOutput),
      temperature: Math.round(temperature),
      vibration: Math.round(vibration * 10) / 10,
      status,
    });
  }
  
  return data;
}

export function analyzeAlerts(data: TurbineDataPoint[]): TurbineAlert[] {
  const alerts: TurbineAlert[] = [];
  const latestData = data[data.length - 1];
  
  if (latestData.temperature > 70) {
    alerts.push({
      id: 'temp-1',
      type: 'high_temp',
      severity: latestData.temperature > 75 ? 'critical' : 'warning',
      message: `High temperature detected: ${latestData.temperature}°C (threshold: 70°C)`,
      timestamp: latestData.timestamp,
    });
  }
  
  if (latestData.vibration > 4.0) {
    alerts.push({
      id: 'vib-1',
      type: 'high_vibration',
      severity: latestData.vibration > 4.5 ? 'critical' : 'warning',
      message: `Elevated vibration levels: ${latestData.vibration} (threshold: 4.0)`,
      timestamp: latestData.timestamp,
    });
  }
  
  // Check for performance degradation
  const recentData = data.slice(-12);
  const avgRecentPower = recentData.reduce((sum, d) => sum + d.power_output, 0) / recentData.length;
  const olderData = data.slice(-24, -12);
  const avgOlderPower = olderData.reduce((sum, d) => sum + d.power_output, 0) / olderData.length;
  
  if (avgOlderPower > 0 && (avgOlderPower - avgRecentPower) / avgOlderPower > 0.15) {
    const degradation = Math.round(((avgOlderPower - avgRecentPower) / avgOlderPower) * 100);
    alerts.push({
      id: 'perf-1',
      type: 'low_performance',
      severity: 'warning',
      message: `Power output declining: ${degradation}% drop over past 12 hours`,
      timestamp: latestData.timestamp,
    });
  }
  
  return alerts;
}

export function calculateMetrics(data: TurbineDataPoint[]) {
  const latestData = data[data.length - 1];
  const avgPower = Math.round(data.reduce((sum, d) => sum + d.power_output, 0) / data.length);
  const avgWindSpeed = Math.round((data.reduce((sum, d) => sum + d.wind_speed, 0) / data.length) * 10) / 10;
  
  return {
    avgPower,
    avgWindSpeed,
    currentStatus: latestData.status,
    currentPower: latestData.power_output,
    currentWindSpeed: latestData.wind_speed,
    currentTemp: latestData.temperature,
    currentVibration: latestData.vibration,
  };
}
