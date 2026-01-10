import { useState, useEffect } from "react";
import { Wind, Zap, Activity, TrendingUp, Gauge, ThermometerSun, ArrowLeft } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { PowerChart } from "@/components/PowerChart";
import { WindPowerScatter } from "@/components/WindPowerScatter";
import { AlertSection } from "@/components/AlertSection";
import { generateTurbineData, analyzeAlerts, calculateMetrics, TurbineDataPoint } from "@/lib/turbineData";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Dashboard = () => {
  const [turbineData, setTurbineData] = useState<TurbineDataPoint[]>([]);
  const [activeChart, setActiveChart] = useState<'power' | 'scatter'>('power');

  useEffect(() => {
    const data = generateTurbineData();
    setTurbineData(data);
  }, []);

  if (turbineData.length === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-pulse">Loading turbine data...</div>
      </div>
    );
  }

  const alerts = analyzeAlerts(turbineData);
  const metrics = calculateMetrics(turbineData);

  return (
    <div className="min-h-screen p-4 lg:p-8 relative overflow-hidden" style={{
      background: 'linear-gradient(135deg, hsl(280, 60%, 20%) 0%, hsl(220, 60%, 25%) 25%, hsl(180, 50%, 30%) 50%, hsl(280, 50%, 25%) 75%, hsl(320, 50%, 20%) 100%)'
    }}>
      {/* Animated glow effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 right-1/3 w-72 h-72 bg-pink-500/15 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <div className="mx-auto max-w-[1800px] space-y-6 relative z-10">
        {/* Header with back button */}
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="outline" size="icon" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              Performance Dashboard
            </h1>
            <p className="text-white/70 mt-1">Detailed analytics and monitoring</p>
          </div>
        </div>

        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Average Power"
            value={metrics.avgPower}
            unit="kW"
            icon={Zap}
            className="bg-gradient-to-br from-amber-500/30 to-orange-600/30 border-amber-500/40 text-slate-900"
          />
          <MetricCard
            title="Average Wind Speed"
            value={metrics.avgWindSpeed}
            unit="m/s"
            icon={Wind}
            className="bg-gradient-to-br from-cyan-500/30 to-blue-600/30 border-cyan-500/40 text-slate-900"
          />
          <MetricCard
            title="Peak Power"
            value={Math.max(...turbineData.map(d => d.power_output)).toFixed(0)}
            unit="kW"
            icon={TrendingUp}
            className="bg-gradient-to-br from-green-500/30 to-emerald-600/30 border-green-500/40 text-slate-900"
          />
          <MetricCard
            title="Efficiency"
            value={(metrics.avgPower / 3000 * 100).toFixed(1)}
            unit="%"
            icon={Gauge}
            className="bg-gradient-to-br from-purple-500/30 to-pink-600/30 border-purple-500/40 text-slate-900"
          />
        </div>

        {/* Chart Toggle Buttons */}
        <div className="flex justify-center gap-4">
          <Button
            variant={activeChart === 'power' ? 'default' : 'outline'}
            onClick={() => setActiveChart('power')}
            className={activeChart === 'power' 
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 border-0' 
              : 'bg-white/10 border-white/20 text-white hover:bg-white/20'
            }
          >
            Power Output Over Time
          </Button>
          <Button
            variant={activeChart === 'scatter' ? 'default' : 'outline'}
            onClick={() => setActiveChart('scatter')}
            className={activeChart === 'scatter' 
              ? 'bg-gradient-to-r from-cyan-500 to-blue-500 border-0' 
              : 'bg-white/10 border-white/20 text-white hover:bg-white/20'
            }
          >
            Wind Speed vs Power Output
          </Button>
        </div>

        {/* Selected Chart */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
          {activeChart === 'power' ? (
            <PowerChart data={turbineData} />
          ) : (
            <WindPowerScatter data={turbineData} />
          )}
        </div>

        {/* Alerts */}
        <AlertSection alerts={alerts} />
      </div>
    </div>
  );
};

export default Dashboard;
