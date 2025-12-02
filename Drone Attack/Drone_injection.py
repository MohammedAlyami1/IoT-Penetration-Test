#!/usr/bin/env python3
"""
E88 Drone - Raw 802.11 Injection with Live Keyboard Control
Combines Scapy packet injection with real-time keyboard interface
"""

from scapy.all import *
import time
import sys
import threading
from pynput import keyboard

class E88ScapyController:
    """
    Keyboard-controlled drone using raw 802.11 frame injection
    """
    
    def __init__(self, 
                 drone_mac="08:17:91:4B:8C:64",
                 interface="wlan0",
                 spoofed_client_mac="EA:9C:F0:89:44:15",
                 drone_ip="192.168.1.1",
                 spoofed_ip="192.168.1.100",
                 control_port=7099):
        
        # Network configuration
        self.drone_mac = drone_mac
        self.interface = interface
        self.spoofed_client_mac = spoofed_client_mac
        self.drone_ip = drone_ip
        self.spoofed_ip = spoofed_ip
        self.control_port = control_port
        
        print(f"[✓] Scapy Controller initialized")
        print(f"    Drone MAC: {self.drone_mac}")
        print(f"    Interface: {self.interface}")
        print(f"    Spoofed Client: {self.spoofed_client_mac}")
        
        # Control state (same as before)
        self.roll = 0x80
        self.pitch = 0x80
        self.throttle = 0x80
        self.yaw = 0x80
        self.flag1 = 0x40
        self.flag2 = 0x40
        
        # Active keys tracking
        self.active_keys = set()
        
        # Control loop management
        self.running = False
        self.armed = False
        self.control_thread = None
        
        # Statistics
        self.packets_sent = 0
        self.injection_errors = 0
        
        # Sequence number for 802.11 frames
        self.sequence = 0

    # Control parameters
    STEP_SIZE = 0x20
    MAX_VALUE = 0xFF
    MIN_VALUE = 0x00
    CENTER_VALUE = 0x80

    def _build_packet(self):
        """
        Build 9-byte control packet (same as before)
        """
        payload = bytes([
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
        return payload

    def _build_802_11_frame(self, payload):
        """
        Wrap payload in 802.11 frame for injection
        
        Frame structure:
        RadioTap → 802.11 Header → LLC/SNAP → IP → UDP → Payload
        """
        
        # 1. RadioTap Header (physical layer info)
        radiotap = RadioTap()

        # 2. 802.11 MAC Header (Data frame going TO the AP/Drone)
        dot11 = Dot11(
            type=2,                      # Data frame
            subtype=0,                   # Data
            FCfield='to-DS',             # Going TO Distribution System (AP)
            addr1=self.drone_mac,        # Receiver (Drone)
            addr2=self.spoofed_client_mac,  # Transmitter (us, spoofed)
            addr3=self.drone_mac         # Final destination
        )
        
        # Increment sequence number
        dot11.SC = self.sequence << 4
        self.sequence = (self.sequence + 1) % 4096  # 12-bit sequence

        # 3. LLC/SNAP Header (bridge between WiFi and IP)
        llc_snap = LLC(dsap=0xaa, ssap=0xaa, ctrl=3) / SNAP(OUI=0x000000, code=0x0800)

        # 4. IP Layer
        ip = IP(src=self.spoofed_ip, dst=self.drone_ip)

        # 5. UDP Layer
        udp = UDP(sport=55555, dport=self.control_port)

        # 6. Combine everything
        return radiotap / dot11 / llc_snap / ip / udp / Raw(load=payload)

    def _send_current_state(self):
        """
        Send current control state via raw 802.11 injection
        """
        try:
            # Build control payload
            payload = self._build_packet()
            
            # Wrap in 802.11 frame
            frame = self._build_802_11_frame(payload)
            
            # Inject at Layer 2
            sendp(frame, iface=self.interface, verbose=0)
            self.packets_sent += 1
            
        except Exception as e:
            self.injection_errors += 1
            if self.injection_errors % 100 == 0:  # Only print every 100 errors
                print(f"\n[!] Injection error #{self.injection_errors}: {e}")

    def _control_loop(self):
        """
        Main control loop - injects frames at 50Hz
        """
        while self.running:
            self._send_current_state()
            time.sleep(0.02)  # 50Hz

    def _update_display(self):
        """
        Display current control state (same as before)
        """
        # Clear screen
        print("\033[2J\033[H", end="")
        
        print("=" * 70)
        print("  E88 DRONE - SCAPY RAW INJECTION CONTROL")
        print("=" * 70)
        
        # Status
        status = "ARMED & FLYING" if self.armed else "STANDBY"
        print(f"\nStatus: {status}")
        print(f"Packets Injected: {self.packets_sent}")
        print(f"Injection Errors: {self.injection_errors}")
        print(f"Sequence Number: {self.sequence}")
        
        # Network info
        print(f"\nNetwork:")
        print(f"  Interface: {self.interface}")
        print(f"  Drone MAC: {self.drone_mac}")
        print(f"  Spoofed MAC: {self.spoofed_client_mac}")
        
        # Control values
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
        print("  SPACE         - Throttle Up")
        print("  SHIFT         - Throttle Down")
        print("  Q/E           - Yaw Left/Right")
        print("  T             - Takeoff")
        print("  L             - Land")
        print("  A             - Arm/Disarm Motors")
        print("  ESC           - Emergency Stop & Exit")
        print("=" * 70)

    def _make_bar(self, value):
        """Create visual bar representation"""
        bar_length = int((value / 255) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
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
            
            # Throttle
            elif key == keyboard.Key.space:
                self.throttle = min(self.MAX_VALUE, self.throttle + self.STEP_SIZE)
                self.active_keys.add("SPACE")
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self.throttle = max(self.MIN_VALUE, self.throttle - self.STEP_SIZE)
                self.active_keys.add("SHIFT")
            
            # Yaw
            elif hasattr(key, 'char'):
                if key.char == 'q':
                    self.yaw = max(self.MIN_VALUE, self.yaw - self.STEP_SIZE)
                    self.active_keys.add("Q")
                elif key.char == 'e':
                    self.yaw = min(self.MAX_VALUE, self.yaw + self.STEP_SIZE)
                    self.active_keys.add("E")
                
                # Takeoff
                elif key.char == 't':
                    if not self.armed:
                        print("\n[!] Must arm motors first (press A)")
                    else:
                        self.flag1 = 0x41
                        self.active_keys.add("TAKEOFF")
                        time.sleep(0.1)
                        self.flag1 = 0x40
                
                # Land
                elif key.char == 'l':
                    self.flag1 = 0x42
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
                return False
            
            self._update_display()
            
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release - return to center"""
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
        for _ in range(25):
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
        for _ in range(50):
            self._send_current_state()
            time.sleep(0.02)

    def _emergency_stop(self):
        """Emergency stop - land immediately"""
        self.flag1 = 0x42
        self._reset_controls()
        
        for _ in range(100):
            self._send_current_state()
            time.sleep(0.01)
        
        self.running = False

    def start(self):
        """Start the keyboard control system"""
        print("\n[*] Starting Scapy injection control...")
        print("[*] Sending handshake frames...")
        
        # Send neutral packets to establish connection
        self._reset_controls()
        for _ in range(50):
            self._send_current_state()
            time.sleep(0.02)
        
        print(f"[✓] Sent {self.packets_sent} handshake frames")
        
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
        
        print("\n[✓] Control system stopped")

if __name__ == "__main__":
    print("=" * 70)
    print("  E88 DRONE - SCAPY RAW 802.11 INJECTION CONTROL")
    print("=" * 70)
    
    print("\n[!] ROOT PRIVILEGES REQUIRED:")
    print("    This script uses raw packet injection")
    print("    Run with: sudo python3 scapy_controller.py")
    
    print("\n[!] MONITOR MODE REQUIRED:")
    print("    Put your wireless interface in monitor mode:")
    print("    sudo airmon-ng start wlan0")
    print("    This creates wlan0 interface")
    
    print("\n[!] CONFIGURATION:")
    print("    Edit the script to set:")
    print("    - DRONE_MAC: Your drone's BSSID")
    print("    - INTERFACE: Your monitor mode interface (wlan0)")
    print("    - SPOOFED_CLIENT_MAC: MAC to spoof")
    
    print("\n[!] ADVANTAGES OF SCAPY METHOD:")
    print("    ✓ Can hijack drone from another controller")
    print("    ✓ Don't need to connect to drone's WiFi")
    print("    ✓ Works even if phone is connected")
    print("    ✓ Can spoof any client MAC address")
    print("    ✓ More stealthy (no association needed)")
    
    print("\n[!] SAFETY:")
    print("    ⚠ More powerful = more responsibility")
    print("    ⚠ Keep hands clear of propellers")
    print("    ⚠ Fly in open space")
    print("    ⚠ ESC key for emergency stop")
    
    # Configuration (edit these values)
    DRONE_MAC = "08:17:91:4B:8C:64"  # CHANGE THIS
    INTERFACE = "wlan0"            # CHANGE THIS
    SPOOFED_CLIENT_MAC = "EA:9C:F0:89:44:15"  # CHANGE THIS
    
    print("\n[?] Current Configuration:")
    print(f"    Drone MAC: {DRONE_MAC}")
    print(f"    Interface: {INTERFACE}")
    print(f"    Spoofed MAC: {SPOOFED_CLIENT_MAC}")
    
    print("\n[!] Is this configuration correct?")
    print("    Press ENTER to start, or Ctrl+C to abort and edit...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n[*] Aborted. Edit the script with correct values.")
        sys.exit(0)
    
    # Check if running as root
    if os.geteuid() != 0:
        print("\n[✗] ERROR: This script must be run as root")
        print("    Run: sudo python3 scapy_controller.py")
        sys.exit(1)
    
    try:
        controller = E88ScapyController(
            drone_mac=DRONE_MAC,
            interface=INTERFACE,
            spoofed_client_mac=SPOOFED_CLIENT_MAC
        )
        controller.start()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted - Landing...")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[✓] Program terminated")
