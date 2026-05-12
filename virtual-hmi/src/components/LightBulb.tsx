"use client";

interface LightBulbProps {
  isOn: boolean;
}

export function LightBulb({ isOn }: LightBulbProps) {
  return (
    <div className="relative flex flex-col items-center justify-center m-2">
      {/* Bulb Glow Aura */}
      <div 
        className={`absolute top-0 w-32 h-32 rounded-full transition-all duration-300 pointer-events-none ${
          isOn ? 'bg-amber-400/70 blur-[50px] scale-150' : 'bg-transparent scale-100 blur-[0px]'
        }`} 
      />
      
      {/* Bulb Glass - Clearly visible even when OFF */}
      <div 
        className={`w-20 h-28 md:w-28 md:h-36 rounded-t-full rounded-b-3xl relative flex items-center justify-center transition-all duration-300 border-2 z-10 ${
          isOn 
            ? 'bg-yellow-100/90 border-yellow-200 shadow-[0_0_80px_rgba(253,224,71,1),inset_0_0_30px_rgba(255,255,255,1)]' 
            : 'bg-gray-800/80 border-gray-500 shadow-[inset_0_0_30px_rgba(0,0,0,1)] backdrop-blur-md'
        }`}
      >
        {/* Filament */}
        <div className={`w-6 h-12 md:w-8 md:h-16 border-x-2 border-t-2 rounded-t-xl absolute bottom-4 transition-colors duration-200 ${
          isOn ? 'border-white shadow-[0_0_20px_rgba(255,255,255,1)] bg-yellow-50/50' : 'border-gray-600'
        }`} />
        
        {/* Glass Reflection */}
        <div className="absolute top-2 left-2 w-4 h-12 bg-white/20 rounded-full blur-[1px] transform -rotate-12 pointer-events-none" />
      </div>

      {/* Base */}
      <div className="w-12 h-10 md:w-16 md:h-12 bg-gradient-to-b from-gray-500 to-gray-800 rounded-b-xl border-t-2 border-gray-900 mt-[-4px] relative z-20 flex flex-col items-center justify-evenly py-1 shadow-2xl">
        <div className="w-full h-[2px] bg-black/60" />
        <div className="w-full h-[2px] bg-black/60" />
        <div className="w-full h-[2px] bg-black/60" />
        <div className="w-4 h-2 md:w-6 md:h-3 bg-gray-900 rounded-b-full mt-1" />
      </div>
    </div>
  );
}
