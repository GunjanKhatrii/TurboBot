import { useState, useEffect } from "react";
import { Fan, LayoutDashboard } from "lucide-react";
import { ChatInterface } from "@/components/ChatInterface";
import { generateTurbineData, TurbineDataPoint } from "@/lib/turbineData";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import AnimatedBackground from "@/components/AnimatedBackground";

const Index = () => {
  const [turbineData, setTurbineData] = useState<TurbineDataPoint[]>([]);

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

  return (
    <div className="min-h-screen bg-background p-4 lg:p-8 border-8 border-page-border relative overflow-hidden flex flex-col">
      <AnimatedBackground />
      
      {/* Background decorative turbine - top right corner */}
      <Fan 
        className="absolute -top-[400px] -right-[400px] h-[1000px] w-[1000px] text-page-border opacity-15 animate-spin pointer-events-none" 
        style={{ animationDuration: '8s' }} 
      />
      
      <div className="mx-auto max-w-[1800px] w-full space-y-4 relative z-10 flex-1 flex flex-col min-h-0">
        {/* Header with navigation button */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-playfair font-bold tracking-tight">
            Wind Turbine Performance Monitor
          </h1>
          <Link to="/dashboard">
            <Button 
              size="sm" 
              className="bg-gradient-to-r from-page-border to-primary hover:opacity-90 transition-opacity shadow-lg"
            >
              <LayoutDashboard className="mr-2 h-4 w-4" />
              Dashboard
            </Button>
          </Link>
        </div>

        {/* TurboBot - fills available space */}
        <div className="flex-1 flex flex-col min-h-0">
          <ChatInterface turbineData={turbineData} />
        </div>
      </div>
    </div>
  );
};

export default Index;
