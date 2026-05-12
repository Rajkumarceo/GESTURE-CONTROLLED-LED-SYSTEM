import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import serial
import threading
import time
import numpy as np
from collections import deque
import asyncio
import websockets
import json

HAND_CONNECTIONS = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]

class WebSocketManager:
    """Broadcasts vision state to the Next.js Virtual Arduino UI."""
    def __init__(self, host='127.0.0.1', port=8765):
        self.host = host
        self.port = port
        self.state_to_send = 0x00
        self.fps = 0
        self.clients = set()
        self.loop = None
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self._start_server, daemon=True)
        self.thread.start()

    def _start_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def run_server():
            try:
                async with websockets.serve(self._handler, self.host, self.port):
                    print(f"WebSocket Server linked on ws://{self.host}:{self.port}", flush=True)
                    await asyncio.Future()  # run forever
            except Exception as e:
                print(f"WebSocket server error: {e}", flush=True)
                
        self.loop.run_until_complete(run_server())

    async def _handler(self, websocket, path=None):
        self.clients.add(websocket)
        try:
            while True:
                await asyncio.sleep(0.05)
                data = json.dumps({"type": "state", "value": self.state_to_send, "fps": int(self.fps)})
                await websocket.send(data)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception:
            pass
        finally:
            self.clients.remove(websocket)

    def update_state(self, state_byte, fps):
        self.state_to_send = state_byte
        self.fps = fps

class SerialManager:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.state_to_send = 0x00
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=0.1)
            print(f"Connected to Arduino on {self.port}")
        except Exception as e:
            pass # Silent ignore for virtual lab
        
        self.running = True
        self.thread = threading.Thread(target=self._send_loop, daemon=True)
        self.thread.start()

    def update_state(self, state_byte):
        with self.lock:
            self.state_to_send = state_byte

    def _send_loop(self):
        while self.running:
            with self.lock:
                state = self.state_to_send
            
            if self.serial and self.serial.is_open:
                packet = bytearray([0x53, state, 0x45])
                try:
                    self.serial.write(packet)
                except serial.SerialException:
                    pass
            time.sleep(0.05)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.serial and self.serial.is_open:
            self.serial.write(bytearray([0x53, 0x00, 0x45]))
            self.serial.close()

class HandController:
    def __init__(self, base_confidence=0.7):
        self.base_confidence = base_confidence
        self.current_confidence = base_confidence
        self.hands = self._init_model(self.base_confidence)
        self.last_brightness = -1

    def _init_model(self, confidence):
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=confidence,
            min_hand_presence_confidence=confidence,
            min_tracking_confidence=confidence
        )
        return vision.HandLandmarker.create_from_options(options)

    def process(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        if self.last_brightness == -1 or abs(brightness - self.last_brightness) > 30:
            target_confidence = np.clip(self.base_confidence * (brightness / 120.0), 0.4, 0.9)
            if abs(target_confidence - self.current_confidence) > 0.15:
                self.hands.close()
                self.current_confidence = target_confidence
                self.hands = self._init_model(self.current_confidence)
                self.last_brightness = brightness

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.hands.detect(mp_image)
        return results, brightness

class Debouncer:
    def __init__(self, history_size=2):
        self.history = deque(maxlen=history_size)
        self.current_state = 0x00

    def update(self, raw_state):
        self.history.append(raw_state)
        if len(self.history) == self.history.maxlen and len(set(self.history)) == 1:
            self.current_state = raw_state
        return self.current_state

class Visualizer:
    @staticmethod
    def draw_hud(frame, results, led_state, fps, brightness):
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (380, 160), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Light: {int(brightness)}", (150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        handedness_texts = []
        if results and results.handedness:
            for h in results.handedness:
                handedness_texts.append(h[0].category_name)
        
        hands_display = " & ".join(handedness_texts) if handedness_texts else "Scanning..."
        cv2.putText(frame, f"Hand: {hands_display}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(frame, "Hardware Out:", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        for i in range(5):
            x_pos = 180 + (i * 35)
            y_pos = 120
            is_on = (led_state & (1 << i))
            
            if is_on: 
                cv2.circle(frame, (x_pos, y_pos), 12, (0, 255, 0), -1) 
                cv2.circle(frame, (x_pos, y_pos), 16, (100, 255, 100), 2)
            else: 
                cv2.circle(frame, (x_pos, y_pos), 10, (80, 80, 80), -1)
                cv2.circle(frame, (x_pos, y_pos), 10, (200, 200, 200), 1)

        if results and results.hand_landmarks:
            h, w, c = frame.shape
            for hand_landmarks in results.hand_landmarks:
                for connection in HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    start_point = (int(hand_landmarks[start_idx].x * w), int(hand_landmarks[start_idx].y * h))
                    end_point = (int(hand_landmarks[end_idx].x * w), int(hand_landmarks[end_idx].y * h))
                    cv2.line(frame, start_point, end_point, (255, 255, 255), 2)
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 2, (0, 200, 255), 2)
        return frame

def calculate_led_state(results):
    state = 0x00
    if not results or not results.hand_landmarks:
        return state
        
    hand = results.hand_landmarks[0]
    
    def dist(idx1, idx2):
        return ((hand[idx1].x - hand[idx2].x)**2 + (hand[idx1].y - hand[idx2].y)**2)**0.5
        
    fingers = []
    # Thumb (Bit 0): Check distance to pinky base vs MCP distance to pinky base
    fingers.append(dist(4, 17) > dist(2, 17))
    
    # Index, Middle, Ring, Pinky (Bits 1-4)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for tip, pip in zip(tips, pips):
        fingers.append(hand[tip].y < hand[pip].y)
        
    for i, is_up in enumerate(fingers):
        if is_up:
            state |= (1 << i)
            
    return state

def main():
    cap = cv2.VideoCapture(0)
    controller = HandController()
    debouncer = Debouncer()
    visualizer = Visualizer()
    
    serial_manager = SerialManager(port='COM3', baudrate=115200) 
    serial_manager.start()

    # 1. Start the WebSocket server to broadcast to Next.js UI
    ws_manager = WebSocketManager(host='127.0.0.1', port=8765)
    ws_manager.start()

    prev_time = time.time()
    fps = 0

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success: break
            
            frame = cv2.flip(frame, 1) 

            results, brightness = controller.process(frame)
            raw_state = calculate_led_state(results)
            stable_state = debouncer.update(raw_state)
            
            # Send to Physical Arduino
            serial_manager.update_state(stable_state)

            curr_time = time.time()
            if (curr_time - prev_time) > 0:
                fps = 1 / (curr_time - prev_time)
            prev_time = curr_time

            # Send to Virtual Arduino UI
            ws_manager.update_state(stable_state, fps)

            frame = visualizer.draw_hud(frame, results, stable_state, fps, brightness)
            cv2.imshow('HMI Core', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        serial_manager.stop()

if __name__ == '__main__':
    main()
