"use client";
import { usePythonVision } from "@/hooks/usePythonVision";
import { LightBulb } from "@/components/LightBulb";
import { ArduinoBoard } from "@/components/ArduinoBoard";

export default function Home() {
  const { isConnected, gestureState } = usePythonVision();

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center overflow-hidden relative font-mono">
      
      {/* Blueprint Background Grid */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.05]" 
           style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

      {!isConnected && (
        <div className="absolute top-10 flex flex-col items-center gap-2 z-50">
          <div className="px-6 py-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm shadow-xl backdrop-blur-md font-bold tracking-wider uppercase">
            Run <code className="bg-black/50 px-2 py-1 mx-1 rounded text-white border border-white/10">python MAIN.PY</code> to establish sensor uplink
          </div>
        </div>
      )}

      {/* Main Schematic Area */}
      <div className="relative w-full max-w-5xl h-[700px] flex flex-col items-center justify-between z-10 pt-10">
        
        {/* The 5 Bulbs */}
        <div className="flex gap-4 md:gap-12 items-center justify-center w-full relative z-20">
          {gestureState.leds.map((isOn, idx) => (
            <div key={idx} className="flex flex-col items-center">
              <LightBulb isOn={isOn} />
              
              {/* Wiring visual */}
              <div className="flex flex-col items-center mt-4">
                <div className={`w-1 h-32 transition-all duration-300 ${isOn ? 'bg-red-500 shadow-[0_0_15px_rgba(239,68,68,1)]' : 'bg-gray-800'}`} />
                <div className="mt-2 px-2 py-1 bg-black border border-white/20 rounded">
                  <span className="text-[10px] text-white font-bold tracking-widest">PIN {idx + 2}</span>
                </div>
                <div className={`w-0.5 h-16 transition-all duration-300 mt-2 ${isOn ? 'bg-red-500' : 'bg-gray-800'}`} />
              </div>
            </div>
          ))}
        </div>

        {/* The Arduino Board */}
        <div className="relative z-30 mt-[-60px]">
          <ArduinoBoard />
        </div>

      </div>
    </div>
  );
}
