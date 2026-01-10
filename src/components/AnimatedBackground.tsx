import { useEffect, useState } from "react";

interface Orb {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
  opacity: number;
}

const AnimatedBackground = () => {
  const [orbs, setOrbs] = useState<Orb[]>([]);

  useEffect(() => {
    const generateOrbs = () => {
      const newOrbs: Orb[] = [];
      for (let i = 0; i < 6; i++) {
        newOrbs.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: 200 + Math.random() * 300,
          duration: 20 + Math.random() * 15,
          delay: Math.random() * -20,
          opacity: 0.03 + Math.random() * 0.05,
        });
      }
      setOrbs(newOrbs);
    };
    generateOrbs();
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
      {/* Base gradient - steel blue to powder blue */}
      <div 
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(to top, hsl(207, 44%, 49%), hsl(200, 50%, 80%))'
        }}
      />
      
      {/* Animated mesh grid */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(hsl(var(--primary) / 0.3) 1px, transparent 1px),
            linear-gradient(90deg, hsl(var(--primary) / 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />
      
      {/* Floating orbs */}
      {orbs.map((orb) => (
        <div
          key={orb.id}
          className="absolute rounded-full blur-3xl animate-float"
          style={{
            left: `${orb.x}%`,
            top: `${orb.y}%`,
            width: `${orb.size}px`,
            height: `${orb.size}px`,
            background: `radial-gradient(circle, hsl(var(--primary) / ${orb.opacity}) 0%, transparent 70%)`,
            animationDuration: `${orb.duration}s`,
            animationDelay: `${orb.delay}s`,
          }}
        />
      ))}
      
      {/* Secondary accent orbs */}
      {orbs.slice(0, 3).map((orb) => (
        <div
          key={`accent-${orb.id}`}
          className="absolute rounded-full blur-3xl animate-float-reverse"
          style={{
            right: `${orb.x}%`,
            bottom: `${orb.y}%`,
            width: `${orb.size * 0.7}px`,
            height: `${orb.size * 0.7}px`,
            background: `radial-gradient(circle, hsl(var(--accent) / ${orb.opacity * 0.8}) 0%, transparent 70%)`,
            animationDuration: `${orb.duration * 1.2}s`,
            animationDelay: `${orb.delay - 5}s`,
          }}
        />
      ))}
      
      {/* Subtle vignette */}
      <div className="absolute inset-0 bg-gradient-to-t from-background/50 via-transparent to-background/30" />
    </div>
  );
};

export default AnimatedBackground;
