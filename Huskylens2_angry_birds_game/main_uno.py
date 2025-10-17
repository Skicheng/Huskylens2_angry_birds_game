# main_uno.py
# -*- coding: utf-8 -*-
import json
import math
import threading
import time
import pygame
import serial
import serial.tools.list_ports
from angry_birds_game import AngryBirdsGame

# Configuration
FRAME_W = 320
FRAME_H = 240
LEFT_WEIGHT = 0.85
TOP_WEIGHT  = 0.15
MAX_ANGLE_H_DEG = 45   # Max horizontal aiming angle in degrees
MAX_ANGLE_V_DEG = 45   # Max vertical aiming angle in degrees
AIM_START_DIST_PX = 25
MIN_LAUNCH_POWER = 0
BAUDRATE = 115200
COM_PORT = None
SMOOTH_ALPHA = 0.35
LAUNCH_GUARD_MS = 300
 


def _clip(v, lo, hi): return max(lo, min(hi, v))


def map_power_and_angle_from_box(x, y, frame_w=FRAME_W, frame_h=FRAME_H):
    """
    Map bounding box center (x, y) to launch power and angle.
    """
    x = _clip(x, 0, frame_w - 1)
    y = _clip(y, 0, frame_h - 1)

    # Power increases toward the right; slight boost toward the top
    right_ratio = x / frame_w                  # 0..1, right-most ≈ 1
    top_ratio   = 1.0 - (y / frame_h)          # 0..1, top-most ≈ 1
    power = 100.0 * (LEFT_WEIGHT * right_ratio + TOP_WEIGHT * top_ratio)
    power = _clip(power, 0.0, 100.0)

    # Horizontal angle: more left → more right-aimed (positive)
    h_tilt  = (frame_w / 2 - x) / (frame_w / 2)            # [-1..1] right→left
    h_angle = h_tilt * math.radians(MAX_ANGLE_H_DEG)       # positive = right

    # Vertical angle: higher → more elevation (positive), lower → depression
    v_tilt  = (frame_h / 2 - y) / (frame_h / 2)            # [-1..1] down→up
    v_angle = v_tilt * math.radians(MAX_ANGLE_V_DEG)

    # Composite angle: zero is rightward; upward adds positive
    angle = v_angle + h_angle
    return power, angle





def auto_find_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        desc = f"{p.description} {p.hwid}".lower()
        if any(k in desc for k in ["arduino", "wchusb", "ch340", "usb-serial"]):
            return p.device
    return ports[-1].device if ports else None


class SerialReader(threading.Thread):
    def __init__(self, port, baudrate):
        super().__init__(daemon=True)
        self.port_name = port
        self.baudrate = baudrate
        self.ser = None
        self.running = True
        self.latest = {}

    def run(self):
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    self._open()
                line = self.ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                if line.startswith("{") and line.endswith("}"):
                    self.latest = json.loads(line)
            except Exception:
                try:
                    if self.ser:
                        self.ser.close()
                except Exception:
                    pass
                time.sleep(0.5)

    def _open(self):
        if not self.port_name:
            self.port_name = auto_find_port()
            if not self.port_name:
                raise RuntimeError("No available serial port found")
        self.ser = serial.Serial(self.port_name, self.baudrate, timeout=0.2)
        print(f"🔌 Serial connected: {self.port_name} @ {self.baudrate}")

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()


class UnoHuskyController:
    def __init__(self):
        self.game = AngryBirdsGame()
        port = COM_PORT or auto_find_port()
        if not port:
            raise RuntimeError("No available serial port was found. Please set your COM_PORT")
        self.reader = SerialReader(port, BAUDRATE)
        self.reader.start()

        self.grabbing = False
        self.aiming = False
        self.grab_origin = None
        self._p_smooth = 0.0
        self._a_smooth = 0.0
        self._inited = False
        self._last_aim_power = 0.0
        self._last_aim_angle = 0.0
        self._last_launch_ts = 0.0

    def _smooth(self, p, a):
        if not self._inited:
            self._p_smooth, self._a_smooth = p, a
            self._inited = True
        else:
            self._p_smooth = (1 - SMOOTH_ALPHA) * self._p_smooth + SMOOTH_ALPHA * p
            self._a_smooth = (1 - SMOOTH_ALPHA) * self._a_smooth + SMOOTH_ALPHA * a
        return self._p_smooth, self._a_smooth

    def _handle_serial(self, data):
        gesture = str(data.get("gesture", "none"))
        x = int(data.get("x", FRAME_W // 2))
        y = int(data.get("y", FRAME_H // 2))

        # Fist (start/maintain draw)
        if gesture == "grab":
            if not self.grabbing:
                self.grabbing = True
                self.aiming = False
                self.grab_origin = (x, y)
            else:
                dx = x - self.grab_origin[0]
                dy = y - self.grab_origin[1]
                dist = math.hypot(dx, dy)
                if not self.aiming and dist >= AIM_START_DIST_PX:
                    self.aiming = True

        # Release = launch
        elif gesture == "release":
            should = (
                self.aiming
                and (time.time() * 1000 - self._last_launch_ts) > LAUNCH_GUARD_MS
                and self._last_aim_power >= MIN_LAUNCH_POWER
            )
            params = {
                "power": float(self._last_aim_power),
                "angle": float(self._last_aim_angle),
                "should_launch": bool(should),
            }
            if should:
                self._last_launch_ts = time.time() * 1000
            self.grabbing = False
            self.aiming = False
            return params

        elif gesture == "hand_open":  # Open hand
            self.grabbing = False
            self.aiming = False

        if self.aiming:
            power, angle = map_power_and_angle_from_box(x, y)
            power, angle = self._smooth(power, angle)
            self._last_aim_power, self._last_aim_angle = power, angle
            return {"power": power, "angle": angle, "should_launch": False}
        else:
            return {"power": 0, "angle": 0, "should_launch": False}

    def run(self):
        print("🎮 UNO+HUSKYLENS mode started")
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            data = self.reader.latest or {}
            params = self._handle_serial(data)
            self.game.handle_gesture_input(params)
            self.game.update()
            self.game.draw()

            pygame.display.flip()
            clock.tick(60)

        self.reader.stop()
        pygame.quit()


if __name__ == "__main__":
    try:
        UnoHuskyController().run()
    except Exception as e:
        print("Runtime error:", e)
