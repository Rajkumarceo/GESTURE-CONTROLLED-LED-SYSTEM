"use client";
import { useState, useEffect } from 'react';

export type GestureState = {
  binaryString: string;
  leds: boolean[];
};

export function usePythonVision() {
  const [gestureState, setGestureState] = useState<GestureState>({
    binaryString: '00000',
    leds: [false, false, false, false, false],
  });
  const [fps, setFps] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout;

    const connect = () => {
      ws = new WebSocket('ws://localhost:8765');
      
      ws.onopen = () => setIsConnected(true);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'state') {
            const rawValue = data.value;
            const fpsValue = data.fps;
            
            let binaryStr = "";
            const ledArray: boolean[] = [];
            for (let i = 0; i < 5; i++) {
              const isOn = (rawValue & (1 << i)) !== 0;
              binaryStr += isOn ? "1" : "0";
              ledArray.push(isOn);
            }
            setGestureState({ binaryString: binaryStr, leds: ledArray });
            setFps(fpsValue);
          }
        } catch (e) {
          console.error(e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 2000);
      };
      
      ws.onerror = () => {
        if (ws) ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
    };
  }, []);

  return { isConnected, gestureState, fps };
}
