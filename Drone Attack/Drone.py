#!/usr/bin/env python3
"""
E88 Drone - Live Keyboard Control
Real-time flight control using keyboard input
"""

import socket
import time
import sys
import threading
from pynput import keyboard

class E88KeyboardController:
    """
    Live keyboard control for E88 drone with visual HUD
    """
    
    def __init__(self, drone_ip="192.168.1.1", control_port=7099):
        self.drone_ip = drone_ip
        self.control_port = control_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Socket setup
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind(("", control_port))
            self.sock.settimeout(0.01)
        except OSError as e:
            print(f"[!] Cannot bind to port {control_port}: {e}")
            sys.exit(1)

        print(f"[✓] Connected to drone at {self.drone_ip}:{self.control_port}")

        # Control state
        self.roll = 0x80      # Left/Right: 0x00 (left) to 0xFF (right), 0x80 = center
        self.pitch = 0x80     # Forward/Back: 0x00 (back) to 0xFF (forward), 0x80 = center
        self.throttle = 0x80  # Up/Down: 0x00 (down) to 0xFF (up), 0x80 = center
        self.yaw = 0x80       # Rotation: 0x00 (CCW) to 0xFF (CW), 0x80 = center
        self.flag1 = 0x40     # Command flags
        self.flag2 = 0x40     # Additional flags
        
        # Active keys tracking
        self.active_keys = set()
        
        # Control loop management
        self.running = False
        self.armed = False
        self.control_thread = None
        
        # Statistics
        self.packets_sent = 0
        self.last_telemetry = None

    # Control parameters
    STEP_SIZE = 0x20      # How much to change per key press (32 in decimal)
    MAX_VALUE = 0xFF      # Maximum stick value
    MIN_VALUE = 0x00      # Minimum stick value
    CENTER_VALUE = 0x80   # Center/neutral position

    def _build_packet(self):
        """Build the 9-byte control packet from current state"""
        return bytes([
            0x03,
            0x66,
            self.roll,
            self.pitch,
            self.throttle,
            self.yaw,
            self.flag1,
            self.flag2,
            0x99
        ])

    def _send_current_state(self):
        """Send current control state to drone"""
        packet = self._build_packet()
        try:
            self.sock.sendto(packet, (self.drone_ip, self.control_port))
            self.packets_sent += 1
            
            # Try to receive telemetry
            try:
                data, addr = self.sock.recvfrom(1024)
                self.last_telemetry = data.hex()
            except (socket.timeout, BlockingIOError):
                pass
        except Exception as e:
            print(f"\n[!] Send error: {e}")

    def _control_loop(self):
        """Main control loop - sends packets at 50Hz"""
        while self.running:
            self._send_current_state()
            time.sleep(0.02)  # 50Hz update rate

    def _update_display(self):
        """Display current control state"""
        # Clear screen (ANSI escape codes)
        print("\033[2J\033[H", end="")
        
        print("=" * 70)
        print("  E88 DRONE - LIVE KEYBOARD CONTROL")
        print("=" * 70)
        
        # Status
        status = "ARMED & FLYING" if self.armed else "STANDBY"
        print(f"\nStatus: {status}")
        print(f"Packets Sent: {self.packets_sent}")
        print(f"Last Telemetry: {self.last_telemetry or 'None'}")
        
        # Control values (show as hex and bar)
        print("\n" + "-" * 70)
        print("CONTROLS:")
        print(f"  Roll (←/→):     0x{self.roll:02X}  {self._make_bar(self.roll)}")
        print(f"  Pitch (↑/↓):    0x{self.pitch:02X}  {self._make_bar(self.pitch)}")
        print(f"  Throttle (Space/Shift): 0x{self.throttle:02X}  {self._make_bar(self.throttle)}")
        print(f"  Yaw (Q/E):      0x{self.yaw:02X}  {self._make_bar(self.yaw)}")
        
        # Active keys
        print("\n" + "-" * 70)
        print("ACTIVE KEYS:", ", ".join(self.active_keys) if self.active_keys else "None")
        
        # Controls legend
        print("\n" + "-" * 70)
        print("KEYBOARD CONTROLS:")
        print("  ↑/↓ Arrows    - Pitch Forward/Backward")
        print("  ←/→ Arrows    - Roll Left/Right")
        print("  SPACE         - Throttle Up (Ascend)")
        print("  SHIFT         - Throttle Down (Descend)")
        print("  Q/E           - Yaw Left/Right (Rotate)")
        print("  T             - Takeoff (Auto)")
        print("  L             - Land")
        print("  A             - Arm/Disarm Motors")
        print("  ESC           - Emergency Stop & Exit")
        print("=" * 70)

    def _make_bar(self, value):
        """Create a visual bar representation of a value (0x00 to 0xFF)"""
        # Map 0-255 to 0-20 characters
        bar_length = int((value / 255) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        # Add center marker
        if value == 0x80:
            return f"[{bar}] CENTER"
        elif value < 0x80:
            return f"[{bar}] ◄"
        else:
            return f"[{bar}] ►"

    def _reset_controls(self):
        """Reset all controls to center/neutral"""
        self.roll = 0x80
        self.pitch = 0x80
        self.throttle = 0x80
        self.yaw = 0x80

    def on_press(self, key):
        """Handle key press events"""
        try:
            # Arrow keys
            if key == keyboard.Key.up:
                self.pitch = min(self.MAX_VALUE, self.pitch + self.STEP_SIZE)
                self.active_keys.add("↑")
            elif key == keyboard.Key.down:
                self.pitch = max(self.MIN_VALUE, self.pitch - self.STEP_SIZE)
                self.active_keys.add("↓")
            elif key == keyboard.Key.left:
                self.roll = max(self.MIN_VALUE, self.roll - self.STEP_SIZE)
                self.active_keys.add("←")
            elif key == keyboard.Key.right:
                self.roll = min(self.MAX_VALUE, self.roll + self.STEP_SIZE)
                self.active_keys.add("→")
            
            # Space and Shift for throttle
            elif key == keyboard.Key.space:
                self.throttle = min(self.MAX_VALUE, self.throttle + self.STEP_SIZE)
                self.active_keys.add("SPACE")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.throttle = max(self.MIN_VALUE, self.throttle - self.STEP_SIZE)
                self.active_keys.add("SHIFT")
            
            # Q/E for yaw
            elif hasattr(key, 'char'):
                if key.char == 'q':
                    self.yaw = max(self.MIN_VALUE, self.yaw - self.STEP_SIZE)
                    self.active_keys.add("Q")
                elif key.char == 'e':
                    self.yaw = min(self.MAX_VALUE, self.yaw + self.STEP_SIZE)
                    self.active_keys.add("E")
                
                # Takeoff command
                elif key.char == 't':
                    if not self.armed:
                        print("\n[!] Must arm motors first (press A)")
                    else:
                        self.flag1 = 0x41  # Takeoff flag
                        self.active_keys.add("TAKEOFF")
                        time.sleep(0.1)
                        self.flag1 = 0x40  # Reset flag
                
                # Land command
                elif key.char == 'l':
                    self.flag1 = 0x42  # Land flag
                    self._reset_controls()
                    self.active_keys.add("LAND")
                    time.sleep(0.1)
                    self.flag1 = 0x40
                
                # Arm/Disarm
                elif key.char == 'a':
                    if not self.armed:
                        print("\n[*] Arming motors...")
                        self._arm_sequence()
                        self.armed = True
                        print("[✓] Motors armed!")
                    else:
                        self.armed = False
                        self._reset_controls()
                        print("\n[*] Motors disarmed")
            
            # ESC to exit
            elif key == keyboard.Key.esc:
                print("\n\n[!] ESC pressed - Emergency landing!")
                self._emergency_stop()
                return False  # Stop listener
            
            self._update_display()
            
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release events - return to center"""
        try:
            if key == keyboard.Key.up:
                self.pitch = self.CENTER_VALUE
                self.active_keys.discard("↑")
            elif key == keyboard.Key.down:
                self.pitch = self.CENTER_VALUE
                self.active_keys.discard("↓")
            elif key == keyboard.Key.left:
                self.roll = self.CENTER_VALUE
                self.active_keys.discard("←")
            elif key == keyboard.Key.right:
                self.roll = self.CENTER_VALUE
                self.active_keys.discard("→")
            elif key == keyboard.Key.space:
                self.throttle = self.CENTER_VALUE
                self.active_keys.discard("SPACE")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.throttle = self.CENTER_VALUE
                self.active_keys.discard("SHIFT")
            elif hasattr(key, 'char'):
                if key.char == 'q':
                    self.yaw = self.CENTER_VALUE
                    self.active_keys.discard("Q")
                elif key.char == 'e':
                    self.yaw = self.CENTER_VALUE
                    self.active_keys.discard("E")
            
            self._update_display()
            
        except AttributeError:
            pass

    def _arm_sequence(self):
        """Perform arming sequence: Throttle Up-Down-Up"""
        # Throttle UP
        self.throttle = 0xFF
        for _ in range(25):  # 0.5 seconds
            self._send_current_state()
            time.sleep(0.02)
        
        # Throttle DOWN
        self.throttle = 0x00
        for _ in range(25):
            self._send_current_state()
            time.sleep(0.02)
        
        # Throttle UP
        self.throttle = 0xFF
        for _ in range(25):
            self._send_current_state()
            time.sleep(0.02)
        
        # Return to center
        self.throttle = 0x80
        for _ in range(50):  # 1 second
            self._send_current_state()
            time.sleep(0.02)

    def _emergency_stop(self):
        """Emergency stop - land immediately"""
        self.flag1 = 0x42  # Land flag
        self._reset_controls()
        
        for _ in range(100):
            self._send_current_state()
            time.sleep(0.01)
        
        self.running = False

    def start(self):
        """Start the keyboard control system"""
        print("\n[*] Starting control system...")
        print("[*] Establishing connection with drone...")
        
        # Send neutral packets to establish connection
        self._reset_controls()
        for _ in range(50):
            self._send_current_state()
            time.sleep(0.02)
        
        if self.last_telemetry:
            print(f"[✓] Drone connected! Telemetry: {self.last_telemetry}")
        else:
            print("[!] Warning: No telemetry received (drone may not be responding)")
        
        # Start control loop thread
        self.running = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        
        # Initial display
        self._update_display()
        
        # Start keyboard listener
        print("\n[*] Keyboard control active!")
        print("[*] Press 'A' to arm motors, then 'T' to takeoff")
        
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        
        # Cleanup
        self.running = False
        if self.control_thread:
            self.control_thread.join(timeout=1)
        
        self.sock.close()
        print("\n[✓] Control system stopped")

if __name__ == "__main__":
    print("=" * 70)
    print("  E88 DRONE - LIVE KEYBOARD CONTROL")
    print("=" * 70)
    print("\n[!] SAFETY CHECKLIST:")
    print("  ☑ Connected to drone WiFi")
    print("  ☑ Drone on flat surface")
    print("  ☑ Clear space (2+ meters all directions)")
    print("  ☑ Ready to hit ESC for emergency stop")
    print("  ☑ Official app closed")
    
    print("\n[!] IMPORTANT:")
    print("  • This requires 'pynput' library")
    print("  • Install with: pip install pynput")
    print("  • Press ESC at ANY time for emergency stop")
    print("  • Keep hands away from propellers")
    
    print("\nPress ENTER to start, or Ctrl+C to abort...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)
    
    try:
        controller = E88KeyboardController()
        controller.start()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted - Landing...")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[✓] Program terminated")
