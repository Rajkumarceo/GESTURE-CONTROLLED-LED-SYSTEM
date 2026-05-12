"use client";
import { usePythonVision } from "@/hooks/usePythonVision";

export function ArduinoBoard() {
  const { isConnected } = usePythonVision();
  
  return (
    <div className="relative glass-panel w-96 h-48 rounded-lg border-2 border-teal-900/50 bg-teal-950/40 p-4 shadow-2xl flex flex-col justify-between">
      {/* Arduino Components */}
      <div className="flex justify-between w-full h-8">
        <div className="w-14 h-12 bg-gray-300 rounded shadow-md border-b-4 border-gray-400" /> {/* USB */}
        <div className="w-10 h-10 bg-black rounded-full border-4 border-gray-800" /> {/* Power */}
      </div>
      
      <div className="flex justify-center w-full">
        <div className="w-32 h-12 bg-gray-900 rounded-sm border border-gray-700 flex items-center justify-center">
          <span className="text-[10px] text-gray-500 font-mono rotate-180">ATmega328P</span>
        </div>
      </div>
      
      {/* Digital Pins Header */}
      <div className="absolute top-2 right-4 flex gap-[6px] bg-black p-2 rounded-sm border border-gray-800">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="flex flex-col items-center gap-1">
            <span className="text-[8px] text-gray-600 font-mono">{i}</span>
            <div className="w-2 h-2 rounded-full bg-gray-600 flex items-center justify-center relative">
              <div className="w-1 h-1 bg-black rounded-full" />
            </div>
          </div>
        ))}
      </div>
      
      <div className="absolute bottom-4 right-4 text-right">
        <h3 className="text-3xl font-black text-white tracking-widest opacity-80">UNO</h3>
        <span className="text-[10px] text-gray-400 font-mono tracking-widest uppercase block mt-1">Virtual Lab</span>
      </div>
      
      <div className="absolute left-6 bottom-6 flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.8)]' : 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.8)]'} animate-pulse`} />
        <span className="text-xs text-white font-mono tracking-widest font-bold">{isConnected ? 'DATA RX' : 'NO SIGNAL'}</span>
      </div>
    </div>
  );
}
