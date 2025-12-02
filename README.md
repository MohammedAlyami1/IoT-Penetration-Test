# IoT & Wireless Security Research Toolkit

**⚠️ EDUCATIONAL AND AUTHORIZED TESTING ONLY ⚠️**

This repository contains security research tools developed as part of an academic penetration testing project targeting IoT devices and wireless networks. These scripts are intended **ONLY** for:
- Educational purposes in controlled laboratory environments
- Security research on your own devices
- Authorized penetration testing with explicit written permission
- Demonstrating vulnerabilities to improve IoT security posture

**Using these tools without authorization is illegal and unethical.**

---

## 👥 Authors

**Security Research Team:**
- Meshari Alqahtani
- Hussam Almuqbil
- Mohammed Alyami
- Mohammed Almuhaini

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Testbed Architecture](#testbed-architecture)
3. [Attack Implementation Scenarios](#attack-implementation-scenarios)
4. [Tool Documentation](#tool-documentation)
5. [Requirements](#requirements)
6. [Legal Disclaimer](#legal-disclaimer)

---

## 🔬 Project Overview

This research project demonstrates practical wireless and IoT penetration testing techniques across four distinct attack scenarios. The experiments were conducted in a controlled laboratory environment to identify and document real-world security vulnerabilities in commercial IoT devices.

### Research Objectives

- Demonstrate security weaknesses in consumer IoT devices
- Validate attack vectors identified in prior research (Project 1)
- Develop custom exploitation tools for educational purposes
- Document defense mechanisms and countermeasures

### Attack Categories Implemented

Based on attack categories from Project 1, this toolkit includes:
- **Man-in-the-Middle (MITM)** attacks
- **Deauthentication** attacks
- **Brute-force** credential enumeration
- **Packet injection** techniques
- **Command injection** exploits
- **Rogue Access Point** impersonation

---

## 🏗️ Testbed Architecture

### Hardware Components

#### 1. TP-Link Tapo C500 Wi-Fi Camera
**Purpose:** Primary target for IP camera penetration testing

**Specifications:**
- 1080p Full HD recording
- 340° pan / 90° tilt (PTZ)
- IP65 weatherproof rating
- Night vision up to ~30m
- microSD storage up to 512GB
- ONVIF protocol support (Port 2020)
- RTSP streaming (Port 554)

#### 2. Tenda N300 Wireless Router
**Purpose:** Network infrastructure hub

**Specifications:**
- 300 Mbps Wi-Fi (2.4 GHz)
- 3 × 5 dBi antennas
- DHCP, NAT, firewall support
- WPA2-PSK encryption

#### 3. ALFA Network AWUS036ACS Dual-Band USB Adapter
**Purpose:** Wireless monitoring and packet injection

**Specifications:**
- Dual-band 2.4 GHz & 5 GHz
- 802.11ac support (up to 600 Mbps)
- USB 3.0 interface
- Monitor mode capable
- Compatible with Linux/Kali
- External antenna for improved range

#### 4. ESP32 Development Boards
**Purpose:** IoT sensor network simulation

**Configurations:**
- **ESP32 A (Sensor Unit):** Ultrasonic sensor + temperature sensor
- **ESP32 B (Buzzer Unit):** RGB LED + alarm buzzer
- Both communicate via Wi-Fi TCP protocol (Port 80)

**Specifications:**
- Dual-core 32-bit Xtensa processor
- Built-in Wi-Fi (802.11 b/g/n)
- GPIO pins for sensor integration
- Supports ESP-NOW, MQTT, HTTP

#### 5. ESP32 Marauder V4
**Purpose:** Wireless network testing and deauthentication attacks

**Capabilities:**
- Wi-Fi scanning and monitoring
- Packet capture & analysis
- Deauthentication attack simulation
- Probe request monitoring
- Portable with onboard display

#### 6. E88/Z708 Wi-Fi Drone
**Purpose:** Wireless drone hijacking demonstration

**Specifications:**
- Wi-Fi FPV control (2.4 GHz)
- Proprietary UDP protocol (Port 7099)
- Single-client trust model
- Smartphone app integration
- SSID: WIFI-UFO-648c4b
- IP: 192.168.1.1 (Soft AP)

#### 7. Kali Linux Workstation
**Purpose:** Attack execution platform

**Tools Used:**
- Aircrack-ng suite (airmon-ng, airodump-ng, aireplay-ng)
- Nmap for network reconnaissance
- Wireshark for packet analysis
- Ettercap for MITM attacks
- Hydra for brute-force attempts
- Custom Python scripts (Scapy, pynput, onvif-zeep)

---

## 🎯 Attack Implementation Scenarios

### Scenario 1: IP Camera Compromise

**Target:** TP-Link Tapo C500 Camera  
**Attack Vector:** WPA2 Handshake Capture → ONVIF Credential Enumeration → PTZ Manipulation → DoS

#### Attack Flow

1. **Network Reconnaissance**
   - Enabled monitor mode on wireless adapter
   - Executed `airodump-ng` to identify target AP (Tenda_E47AC8)
   - Captured BSSID and Channel information

2. **WPA2 Handshake Capture**
   - Performed deauthentication attack using `aireplay-ng`
   - Captured 4-way handshake during client reconnection
   - Verified handshake integrity with Wireshark (EAPOL filter)

3. **Password Cracking**
   - Used `aircrack-ng` with custom wordlist
   - Successfully cracked WPA2-PSK password: `Mohammed1234`
   - Gained unauthorized network access

4. **Service Discovery**
   - Executed `nmap` scan on subnet
   - Identified camera at IP 192.168.0.100
   - Discovered open ports:
     - **Port 554:** RTSP (streaming)
     - **Port 2020:** ONVIF (management)

5. **Initial Brute-Force Attempt (Failed)**
   - Attempted Hydra attack on RTSP Port 554
   - **Result:** Failed due to rate-limiting mechanisms
   - **Finding:** Streaming port had stronger protections than expected

6. **ONVIF Credential Enumeration (Success)**
   - Developed custom Python script: `BrutforcePort2020.py`
   - Targeted administrative ONVIF port (2020)
   - Successfully enumerated credentials: `admin1:password123`
   - **Finding:** Administrative port lacked rate-limiting

7. **Live Stream Compromise**
   - Executed: `ffplay rtsp://admin1:password123@192.168.0.100:554/stream1`
   - Gained unauthorized access to live surveillance feed

8. **Physical PTZ Control**
   - Executed `Control.py` script via ONVIF protocol
   - Successfully manipulated Pan/Tilt/Zoom functions
   - Demonstrated physical control over camera orientation

9. **Denial of Service (DoS)**
   - Executed `Reboot.py` script
   - Sent continuous `SystemReboot()` commands
   - Forced camera into infinite reboot loop

#### Key Findings

**Security Paradox Discovered:**
- RTSP Port (554) had **strong rate-limiting** → brute-force resistant
- ONVIF Port (2020) had **no rate-limiting** → vulnerable to enumeration
- Administrative interface was weaker than streaming interface

---

### Scenario 2: IoT Sensor Network Attack

**Target:** ESP32 Sensor (192.168.0.101) → ESP32 Buzzer (192.168.0.103)  
**Attack Vector:** ARP Spoofing → Packet Sniffing → Command Injection → DoS

#### Attack Flow

1. **Network Discovery**
   - Used `netdiscover` to scan subnet (192.168.0.0/24)
   - Identified ESP32 devices by MAC vendor (Espressif Inc.)

2. **MITM Setup (Ettercap)**
   - Launched Ettercap GUI with interface `wlan1`
   - Added Sensor (192.168.0.101) as Target 1
   - Added Buzzer (192.168.0.103) as Target 2
   - Executed ARP poisoning attack

3. **Protocol Reverse Engineering (Wireshark)**
   - Captured unencrypted TCP traffic on Port 80
   - Identified command structure:
     - `TEMP:28.0` → Temperature reading format
     - `ALARM` → Trigger buzzer command
     - `CLEAR` → Silence buzzer command
   - **Vulnerability:** Cleartext protocol, no authentication

4. **Wi-Fi Deauthentication (DoS)**
   - Used `airodump-ng` to identify AP BSSID and channel
   - Executed `aireplay-ng` deauth attack
   - Disconnected legitimate sensor from network

5. **Command Injection Attack**
   - Developed custom script: `Reply.py`
   - Established direct TCP socket to Buzzer (192.168.0.103:80)
   - Successfully injected spoofed commands:
     - Triggered false alarms
     - Silenced legitimate alerts
     - Sent fake temperature readings (`TEMP:60`)

#### Key Findings

**Critical Vulnerabilities:**
- No ARP spoofing protection
- Cleartext TCP communication
- Zero authentication on command channel
- No integrity verification for sensor data

---

### Scenario 3: Drone Hijacking

**Target:** E88 Wi-Fi Drone (SSID: WIFI-UFO-648c4b)  
**Attack Vector:** Protocol Analysis → Deauthentication → Packet Injection → C2 Takeover

#### Attack Flow

1. **Wireless Reconnaissance**
   - Enabled monitor mode: `airmon-ng start wlan0`
   - Scanned 2.4 GHz spectrum: `airodump-ng wlan0mon`
   - Identified drone AP:
     - BSSID: `08:17:91:4B:8C:64`
     - Channel: 1
     - Connected client (pilot): `EA:9C:F0:89:44:15`

2. **Protocol Analysis (Wireshark)**
   - Captured communication on **UDP Port 7099**
   - Reverse-engineered 9-byte control packet:
     ```
     03 66 80 80 80 80 40 40 99
     │  │  │  │  │  │  │  │  └─ End marker
     │  │  │  │  │  │  └─ └─── Flag bytes
     │  │  │  │  └─ └───────── Yaw (rotation)
     │  │  └─ └─────────────── Throttle (up/down)
     │  └─────────────────────  Pitch (forward/back)
     └────────────────────────  Roll (left/right)
     ```
   - 0x80 = neutral/center position
   - Identified telemetry acknowledgment: `53 01 00 00 00`

3. **Identified Attack Vectors**

   **Method 1: Pre-emptive Control (First-Connect)**
   - Drone has "Single-Client" vulnerability
   - Connects before legitimate user
   - Tool: `Drone.py` (standard UDP socket)
   - Result: Full control takeover

   **Method 2: Deauthentication → Takeover**
   - Execute: `aireplay-ng --deauth 0 -a [DRONE_BSSID] -c [PILOT_MAC]`
   - Disconnect legitimate pilot
   - Quickly connect during reconnection window
   - Tool: `Drone.py`

   **Method 3: Raw Packet Injection (Mid-Flight Hijacking)**
   - No need to join drone's Wi-Fi network
   - Spoof pilot's MAC address
   - Inject crafted 802.11 frames
   - Tool: `Drone_injection.py` (Scapy-based)
   - Bypasses "Single-Client" restriction

4. **Successful Execution**
   - Developed custom keyboard control interface
   - Real-time flight commands at 50Hz
   - Successfully armed motors and executed flight maneuvers
   - Demonstrated complete Command & Control (C2) hijack

#### Key Findings

**Critical Vulnerabilities:**
- Unencrypted UDP protocol
- No authentication mechanism
- "First-Connect" trust model
- Unprotected 802.11 management frames
- No MAC address verification
- Bi-directional handshake not cryptographically secured

---

### Scenario 4: Rogue Access Point (Conceptual)

**Note:** This scenario was demonstrated conceptually using ESP32 Marauder V4. Due to hardware limitations, full backend credential capture was not implemented. The focus was on UI deception and captive portal phishing techniques.

**Target:** Mobile users  
**Attack Vector:** Evil Twin AP → Captive Portal Phishing

#### Conceptual Flow

1. Create fake AP mimicking legitimate network (e.g., "KSU Guest")
2. Deploy captive portal with branded login page
3. Users connect believing it's legitimate
4. Credentials submitted to attacker-controlled backend
5. Man-in-the-Middle position established

**Limitations Encountered:**
- ESP32 Marauder cannot run full backend server
- Cannot receive/store submitted credentials
- More advanced hardware required (e.g., Wi-Fi Pineapple)

---

## 📚 Tool Documentation

### IP Camera Attack Tools

#### Control.py - ONVIF Camera PTZ Control

Controls Pan-Tilt-Zoom cameras via ONVIF protocol.

**Configuration:**
```python
YOUR_IP = '192.168.0.100'      # Camera IP
YOUR_PORT = 2020               # ONVIF port
YOUR_USERNAME = 'admin1'       # Camera account
YOUR_PASSWORD = 'password123'  # Password
```

**Movement Commands:**
```python
# Pan/Tilt values: -1.0 to 1.0
move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}   # Right
move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}  # Left
move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}   # Up
move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}}  # Down
```

**Usage:**
```bash
python3 Control.py
```

---

#### BrutforcePort2020.py - ONVIF Credential Testing

Dictionary-based brute-force tool for ONVIF cameras.

**Setup:**

1. Create `user.txt`:
```
admin
admin1
root
user
```

2. Create `pass.txt`:
```
admin
password
12345
password123
```

3. Configure script:
```python
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
USER_FILE = 'user.txt'
PASS_FILE = 'pass.txt'
```

**Usage:**
```bash
python3 BrutforcePort2020.py
```

**Features:**
- Tests all username/password combinations
- Automatically sends reboot command on success
- Progress monitoring for each attempt

---

#### Reboot.py - Continuous Camera DoS

Denial of Service tool via continuous reboot loop.

**Configuration:**
```python
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
YOUR_USERNAME = 'admin1'
YOUR_PASSWORD = 'password123'
```

**Usage:**
```bash
python3 Reboot.py
# Press Ctrl+C to stop
```

**Behavior:**
1. Connects to camera
2. Sends `SystemReboot()` command
3. Waits 25 seconds
4. Repeats indefinitely
5. Keeps camera in perpetual reboot state

---

### IoT Sensor Attack Tools

#### Reply.py - ESP32 Command Injection

TCP socket tool for injecting commands to ESP32 IoT devices.

**Configuration:**
```python
TARGET_IP = "192.168.0.103"  # Buzzer IP
TARGET_PORT = 80              # TCP port
```

**Available Commands:**
- `ALARM` - Trigger buzzer
- `CLEAR` - Silence buzzer
- `TEMP:60` - Send fake temperature reading

**Usage:**
```bash
python3 Reply.py
```

**Menu Options:**
```
--- ESP32 Attack Tool ---
1. Trigger Alarm
2. Silence Alarm
3. Fake Temperature (TEMP>50)

Select attack (1-3):
```

---

### Drone Control & Hijacking Tools

#### Drone.py - Live Keyboard Control

Real-time UDP-based drone control with visual HUD.

**Features:**
- 50Hz packet transmission rate
- Real-time keyboard input processing
- Visual control state display
- Arm/disarm sequence
- Emergency stop (ESC)

**Installation:**
```bash
pip install pynput
```

**Usage:**
```bash
# Connect to drone WiFi first (SSID: WIFI-UFO-648c4b)
python3 Drone.py
```

**Keyboard Controls:**
- `↑/↓` Arrows - Pitch forward/backward
- `←/→` Arrows - Roll left/right
- `SPACE` - Throttle up (ascend)
- `SHIFT` - Throttle down (descend)
- `Q/E` - Yaw left/right (rotate)
- `A` - Arm/disarm motors
- `T` - Takeoff (auto)
- `L` - Land
- `ESC` - Emergency stop & exit

**Control Values:**
- Range: 0x00 to 0xFF (0-255)
- Center: 0x80 (128)
- Step size: 0x20 (32)

---

#### Drone_injection.py - Raw 802.11 Packet Injection

Advanced drone hijacking using Scapy for raw frame injection.

**Advantages:**
- ✓ No need to join drone's Wi-Fi
- ✓ Can hijack mid-flight
- ✓ Bypasses "Single-Client" restriction
- ✓ MAC address spoofing
- ✓ More stealthy operation

**Requirements:**
- Root privileges
- Wireless adapter in monitor mode
- Scapy library

**Setup:**
```bash
# Install dependencies
pip install scapy pynput

# Enable monitor mode
sudo airmon-ng start wlan0

# Edit configuration in script
DRONE_MAC = "08:17:91:4B:8C:64"          # Drone BSSID
INTERFACE = "wlan0mon"                    # Monitor interface
SPOOFED_CLIENT_MAC = "EA:9C:F0:89:44:15" # Pilot MAC to spoof
```

**Usage:**
```bash
sudo python3 Drone_injection.py
```

**Technical Details:**

The script builds complete 802.11 frames:
```
RadioTap → 802.11 Header → LLC/SNAP → IP → UDP → Control Payload
```

**Frame Structure:**
- RadioTap: Physical layer info
- 802.11 Header: MAC addresses, sequence numbers
- LLC/SNAP: Bridge between WiFi and IP
- IP Layer: Spoofed source (pilot) → Drone
- UDP: Port 7099 (control channel)
- Payload: 9-byte control command

---

## 📦 Requirements

### Python Packages

```bash
# Drone control
pip install pynput

# Packet injection
pip install scapy

# IP Camera control
pip install onvif-zeep

# Install all dependencies
pip install pynput scapy onvif-zeep
```

### System Requirements

**For Kali Linux Testbed:**
- Kali Linux 2023.x or later
- Wireless adapter supporting monitor mode (e.g., ALFA AWUS036ACS)
- Root/sudo access
- Aircrack-ng suite
- Nmap, Wireshark, Ettercap

**For Drone Injection:**
- Linux OS (Kali recommended)
- Monitor mode capable adapter
- Scapy with 802.11 support
- Root privileges

**For Camera Tools:**
- Python 3.6+
- Network access to target camera
- ONVIF protocol support on target

**For ESP32 Testing:**
- Network connectivity to ESP32 devices
- TCP socket support

---

## 🛡️ Security Best Practices & Countermeasures

### For IP Camera Owners

**Immediate Actions:**
1. Change default credentials immediately
2. Use strong, unique passwords (16+ characters)
3. Disable ONVIF if not needed
4. Enable rate-limiting on all ports
5. Update firmware regularly
6. Use VLANs to isolate cameras
7. Monitor access logs
8. Implement certificate-based authentication

**Network-Level Protections:**
- Place cameras on dedicated IoT VLAN
- Use firewall rules to restrict access
- Enable intrusion detection systems (IDS)
- Implement 802.1X authentication

---

### For IoT Device Developers

**Communication Security:**
1. **Encrypt all traffic** (TLS/DTLS minimum)
2. **Implement authentication** on all command channels
3. **Use message authentication codes** (HMAC)
4. **Validate all inputs** server-side
5. **Implement ARP spoofing protection**
6. **Use secure protocols** (MQTT with TLS, HTTPS)

**Best Practices:**
- Never use cleartext protocols
- Implement mutual authentication
- Use certificate pinning
- Add replay attack protection
- Include integrity checks
- Log all security events

---

### For Drone Manufacturers

**Critical Fixes Needed:**
1. **Implement encryption** on control protocol (AES-256)
2. **Add authentication** (challenge-response)
3. **Cryptographically bind** controller to drone
4. **Protect management frames** (802.11w)
5. **Implement sequence number validation**
6. **Add MAC address verification**
7. **Use frequency hopping** or channel bonding

**Design Improvements:**
- Multi-factor device pairing
- Encrypted video streams
- Secure boot verification
- Over-the-air update signing
- Tamper detection mechanisms

---

### For Wireless Network Users

**WPA2/WPA3 Security:**
1. Use WPA3 where available
2. Use strong passphrases (20+ characters)
3. Change default SSID
4. Disable WPS
5. Enable MAC address filtering (as additional layer)
6. Use separate guest networks
7. Monitor connected devices

**Detecting Attacks:**
- Monitor for unexpected deauthentication frames
- Watch for duplicate MAC addresses (spoofing)
- Use wireless intrusion detection systems (WIDS)
- Enable logging on access points
- Regular security audits

---

## 📊 Summary of Vulnerabilities & Attack Vectors

| **Scenario** | **Target** | **Attack Vector** | **Vulnerability** | **Impact** |
|-------------|-----------|------------------|------------------|-----------|
| **IP Camera** | TP-Link Tapo C500 | WPA2 Handshake Capture | Weak password complexity | Unauthorized network access |
| | | ONVIF Credential Enumeration | No rate-limiting on Port 2020 | Privilege escalation |
| | | PTZ Manipulation | Unsecured API endpoints | Physical camera control |
| | | DoS (Reboot Loop) | Unrestricted reboot commands | Service disruption |
| **IoT Sensors** | ESP32 Network | ARP Spoofing | No ARP validation | MITM position established |
| | | Packet Sniffing | Cleartext TCP protocol | Command structure exposed |
| | | Command Injection | No authentication | False alarm injection |
| | | Deauthentication | Unprotected 802.11 frames | Device disconnection |
| **Drone** | E88 Wi-Fi Drone | Protocol Analysis | Unencrypted UDP | Control protocol revealed |
| | | Deauthentication | Unprotected management frames | Pilot disconnection |
| | | Packet Injection | No authentication | Mid-flight hijacking |
| | | Pre-emptive Control | "Single-Client" trust model | Complete takeover |
| **Rogue AP** | Mobile Users | Evil Twin AP | No AP authentication | User connection to fake network |
| | | Captive Portal | Visual trust over crypto | Credential theft |

---

## 🎓 Educational Resources

### Understanding the Attacks

**Man-in-the-Middle (MITM):**
- ARP spoofing exploits lack of authentication in Address Resolution Protocol
- Allows attacker to intercept traffic between two parties
- Can modify, inject, or drop packets in real-time

**Deauthentication Attacks:**
- Exploits unprotected 802.11 management frames
- Forces clients to disconnect from AP
- Used for handshake capture or creating takeover windows
- Mitigated by 802.11w (Protected Management Frames)

**Brute-Force Attacks:**
- Dictionary-based password guessing
- Effective against weak passwords
- Mitigated by: strong passwords, rate-limiting, account lockouts

**Packet Injection:**
- Crafting and transmitting raw network packets
- Requires monitor mode and appropriate drivers
- Can spoof source addresses and sequence numbers

**Protocol Reverse Engineering:**
- Analyzing packet captures to understand proprietary protocols
- Identifying command structures and authentication mechanisms
- Critical for developing custom exploitation tools

---

## ⚖️ Legal Disclaimer

### READ THIS CAREFULLY

These tools were developed for an **academic research project** in a **controlled laboratory environment** using **devices owned by the research team**.

**You MAY use these tools:**
- ✅ On devices you own
- ✅ In authorized penetration tests with **written permission**
- ✅ In controlled lab environments
- ✅ For security research and education

**You MAY NOT use these tools:**
- ❌ On devices you don't own without explicit authorization
- ❌ To disrupt services or cause harm
- ❌ To gain unauthorized access to systems
- ❌ For any illegal or malicious purposes
- ❌ Against production systems without permission

**Legal Consequences:**

Unauthorized access to computer systems is illegal under:
- **Computer Fraud and Abuse Act (CFAA)** in the USA
- **Computer Misuse Act** in the UK
- Similar laws in virtually all countries worldwide

Violations can result in:
- Criminal prosecution
- Heavy fines (up to $250,000 USD)
- Imprisonment (up to 20 years)
- Civil liability
- Permanent criminal record

---

## 🛡️ Responsible Disclosure

If you discover vulnerabilities using these tools:

1. **Do not** exploit them maliciously
2. **Do not** publicly disclose without vendor coordination
3. **Do** report to the vendor through proper security channels
4. **Do** allow reasonable time for fixes (typically 90 days)
5. **Do** follow coordinated disclosure guidelines (e.g., CERT/CC)

**Recommended Disclosure Process:**
1. Document the vulnerability thoroughly
2. Contact vendor's security team (security@vendor.com)
3. Provide proof-of-concept (PoC) responsibly
4. Allow 90-day remediation window
5. Coordinate public disclosure with vendor
6. Publish findings only after patch availability

---

## 🤝 Contributing

If you discover improvements or additional security issues:

1. Test responsibly on your own devices
2. Document findings clearly with:
   - Attack scenario description
   - Step-by-step reproduction
   - Impact assessment
   - Proposed mitigations
3. Submit pull requests with detailed descriptions
4. Include responsible disclosure information

---

## 📄 License

These tools are provided "AS IS" for **educational purposes only**. The authors assume **no liability** for misuse. Users are **solely responsible** for complying with all applicable laws and regulations.

**This project is intended for:**
- Academic research
- Security awareness
- Vulnerability demonstration
- Defense improvement

**This project is NOT intended for:**
- Unauthorized access
- Malicious activities
- Production system attacks
- Any illegal purposes

---

## 🙏 Acknowledgments

- **Testing Environment:** All experiments conducted in controlled laboratory
- **Hardware:** Consumer IoT devices purchased for research purposes
- **Tools:** Open-source security tools (Kali Linux, Aircrack-ng, Scapy, Wireshark)
- **Ethical Guidelines:** Followed responsible disclosure and academic integrity standards

---

## 📞 Contact

For questions regarding:
- **Responsible disclosure:** Contact through academic channels
- **Security research collaboration:** Via institutional email
- **Clarifications on attack techniques:** Educational purposes only

**Note:** We do not provide support for using these tools in unauthorized contexts.

---

## ⚠️ Final Warning

**THINK BEFORE YOU ACT**

Before running any of these scripts, ask yourself:

1. ✅ **Do I own this device?**
2. ✅ **Do I have written authorization?**
3. ✅ **Am I in a controlled environment?**
4. ✅ **Do I understand the legal consequences?**
5. ✅ **Is my intent purely educational?**

If you answered **"NO"** to **ANY** of these questions:

# ⛔ DO NOT PROCEED ⛔

---

**Security research is about making systems safer, not causing harm.**

**Stay Curious. Stay Ethical. Stay Legal.** 🔐

---

*Last Updated: December 2024*  
*Project: IoT & Wireless Security Penetration Testing*  
*Purpose: Academic Research & Education*
